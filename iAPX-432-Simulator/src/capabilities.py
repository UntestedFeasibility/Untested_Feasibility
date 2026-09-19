"""
iAPX 432 Capability System

Implements the capability-based security model with
access descriptor validation and protection checks.
"""

from typing import Optional
from .objects import (
    AccessDescriptor, AccessRights, ObjectType,
    Domain, ObjectTable
)


class CapabilityError(Exception):
    """Base class for capability errors"""
    pass


class InvalidAccessDescriptor(CapabilityError):
    """Raised when access descriptor is invalid"""
    pass


class AccessDenied(CapabilityError):
    """Raised when access is denied"""
    pass


class TypeMismatch(CapabilityError):
    """Raised when object type doesn't match expected type"""
    pass


class DomainViolation(CapabilityError):
    """Raised when domain boundary is violated"""
    pass


class CapabilityChecker:
    """
    Capability Checker
    
    Validates access descriptors and enforces protection.
    In iAPX 432, every memory access requires a valid AD.
    """
    
    def __init__(self, object_table: ObjectTable):
        self.object_table = object_table
        self.violations: list = []
    
    def validate_ad(self, ad: AccessDescriptor, 
                    required_type: Optional[ObjectType] = None,
                    required_rights: Optional[AccessRights] = None) -> bool:
        """
        Validate an access descriptor
        
        Args:
            ad: Access descriptor to validate
            required_type: Expected object type (None = any)
            required_rights: Required access rights (None = any)
            
        Returns:
            True if valid, raises exception otherwise
        """
        # Check if AD is valid
        if not ad.valid:
            raise InvalidAccessDescriptor("Access descriptor is not valid")
        
        # Check if object exists
        obj = self.object_table.get_object(ad.object_id)
        if obj is None:
            raise InvalidAccessDescriptor(f"Object {ad.object_id:#x} does not exist")
        
        # Check type match
        if required_type is not None:
            if ad.type != required_type:
                raise TypeMismatch(
                    f"Expected type {required_type.name}, got {ad.type.name}"
                )
        
        # Check access rights
        if required_rights is not None:
            if not self._has_rights(ad.access_rights, required_rights):
                raise AccessDenied(
                    f"Required rights {required_rights.name}, "
                    f"have {ad.access_rights.name}"
                )
        
        return True
    
    def check_read(self, ad: AccessDescriptor) -> bool:
        """Check read access"""
        return self.validate_ad(ad, required_rights=AccessRights.READ)
    
    def check_write(self, ad: AccessDescriptor) -> bool:
        """Check write access"""
        return self.validate_ad(ad, required_rights=AccessRights.WRITE)
    
    def check_execute(self, ad: AccessDescriptor) -> bool:
        """Check execute access"""
        return self.validate_ad(ad, required_rights=AccessRights.EXECUTE)
    
    def check_read_write(self, ad: AccessDescriptor) -> bool:
        """Check read-write access"""
        return self.validate_ad(ad, required_rights=AccessRights.READ_WRITE)
    
    def check_domain_access(self, ad: AccessDescriptor, 
                           current_domain: Domain) -> bool:
        """
        Check if AD can be accessed from current domain
        
        Args:
            ad: Access descriptor to check
            current_domain: Current execution domain
            
        Returns:
            True if access allowed
        """
        # Check if AD is in current domain or parent domain
        if ad.domain_id == current_domain.domain_id:
            return True
        
        # Check parent domain
        if current_domain.parent_domain_id == ad.domain_id:
            return True
        
        # Check child domains
        if ad.domain_id in current_domain.child_domain_ids:
            return True
        
        raise DomainViolation(
            f"AD belongs to domain {ad.domain_id:#x}, "
            f"current domain is {current_domain.domain_id:#x}"
        )
    
    def create_child_domain(self, parent_domain: Domain, 
                           type_manager_id: int) -> Domain:
        """
        Create a child domain
        
        Args:
            parent_domain: Parent domain
            type_manager_id: Type manager for new domain
            
        Returns:
            New domain
        """
        domain_id = self.object_table.create_domain(parent_domain.domain_id)
        new_domain = self.object_table.get_domain(domain_id)
        
        # Create context for new domain
        self.object_table.create_context(domain_id)
        
        return new_domain
    
    def transfer_ad(self, source_domain: Domain, 
                   target_domain: Domain,
                   ad: AccessDescriptor,
                   reduce_rights: bool = False) -> AccessDescriptor:
        """
        Transfer an AD between domains
        
        Args:
            source_domain: Source domain
            target_domain: Target domain
            ad: Access descriptor to transfer
            reduce_rights: If True, reduce access rights
            
        Returns:
            New AD in target domain
        """
        # Verify source domain owns the AD
        self.check_domain_access(ad, source_domain)
        
        # Create new AD for target domain
        new_ad = AccessDescriptor()
        new_ad.object_id = ad.object_id
        new_ad.type = ad.type
        new_ad.access_rights = ad.access_rights
        new_ad.domain_id = target_domain.domain_id
        new_ad.valid = ad.valid
        
        # Optionally reduce rights
        if reduce_rights:
            new_ad.access_rights = self._reduce_rights(ad.access_rights)
        
        # Add to target domain
        target_domain.add_access_descriptor(new_ad)
        
        return new_ad
    
    def _has_rights(self, have: AccessRights, 
                   need: AccessRights) -> bool:
        """Check if we have required rights"""
        return (have.value & need.value) == need.value
    
    def _reduce_rights(self, rights: AccessRights) -> AccessRights:
        """Reduce access rights (e.g., remove WRITE)"""
        new_value = rights.value & ~AccessRights.WRITE.value
        return AccessRights(new_value)
    
    def log_violation(self, violation_type: str, details: str):
        """Log a security violation"""
        self.violations.append({
            'type': violation_type,
            'details': details
        })
    
    def get_violations(self) -> list:
        """Get list of violations"""
        return self.violations
    
    def __repr__(self) -> str:
        return f"CapabilityChecker(violations={len(self.violations)})"
