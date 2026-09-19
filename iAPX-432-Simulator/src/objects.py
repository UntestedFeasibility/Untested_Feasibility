"""
iAPX 432 Object System

Implements the object-oriented memory model with access descriptors,
domains, type management, and protection.
"""

from enum import IntEnum
from typing import Dict, Optional, List
from .memory import Memory


class ObjectType(IntEnum):
    """Object type identifiers"""
    INSTRUCTION = 0x01
    DATA = 0x02
    CAPABILITY = 0x03
    CONTEXT = 0x04
    DOMAIN = 0x05
    TYPE_MANAGER = 0x06
    PROCESS = 0x07
    MARKER = 0x08


class AccessRights(IntEnum):
    """Access rights for objects"""
    NONE = 0x00
    READ = 0x01
    WRITE = 0x02
    EXECUTE = 0x04
    READ_WRITE = 0x03
    READ_EXECUTE = 0x05
    FULL = 0x07


class AccessDescriptor:
    """
    Access Descriptor (AD)
    
    The fundamental capability token in iAPX 432.
    Contains: pointer to object + type + access rights.
    """
    
    def __init__(self):
        self.object_id: int = 0
        self.type: ObjectType = ObjectType.DATA
        self.access_rights: AccessRights = AccessRights.NONE
        self.domain_id: int = 0
        self.valid: bool = False
    
    def encode(self) -> int:
        """Encode AD to 32-bit integer"""
        if not self.valid:
            return 0
        
        encoded = (
            (self.object_id & 0xFFFF) |
            ((self.type & 0xFF) << 16) |
            ((self.access_rights & 0xFF) << 24)
        )
        return encoded
    
    @classmethod
    def decode(cls, value: int) -> 'AccessDescriptor':
        """Decode 32-bit integer to AD"""
        ad = cls()
        ad.object_id = value & 0xFFFF
        ad.type = ObjectType((value >> 16) & 0xFF)
        ad.access_rights = AccessRights((value >> 24) & 0xFF)
        ad.valid = (value != 0)
        return ad
    
    def __repr__(self) -> str:
        if not self.valid:
            return "AD(INVALID)"
        return f"AD(obj={self.object_id:#06x}, type={self.type.name}, rights={self.access_rights.name})"


class Domain:
    """
    Protection Domain
    
    An isolated execution environment with its own
    access descriptors, stack, and instruction space.
    """
    
    def __init__(self, domain_id: int):
        self.domain_id = domain_id
        self.access_descriptors: List[AccessDescriptor] = []
        self.parent_domain_id: Optional[int] = None
        self.child_domain_ids: List[int] = []
        self.created_by: Optional[int] = None
        self.active: bool = True
    
    def add_access_descriptor(self, ad: AccessDescriptor) -> int:
        """Add AD and return its index"""
        idx = len(self.access_descriptors)
        self.access_descriptors.append(ad)
        return idx
    
    def get_access_descriptor(self, index: int) -> Optional[AccessDescriptor]:
        """Get AD by index"""
        if 0 <= index < len(self.access_descriptors):
            return self.access_descriptors[index]
        return None
    
    def remove_access_descriptor(self, index: int) -> bool:
        """Remove AD by index"""
        if 0 <= index < len(self.access_descriptors):
            self.access_descriptors[index].valid = False
            return True
        return False
    
    def __repr__(self) -> str:
        return f"Domain(id={self.domain_id}, ads={len(self.access_descriptors)}, active={self.active})"


class Context:
    """
    Context Object
    
    Provides the execution context for a process:
    - Program counter
    - Stack pointer
    - Current domain
    - Operand stack state
    """
    
    def __init__(self, context_id: int):
        self.context_id = context_id
        self.pc: int = 0
        self.sp: int = 0
        self.domain_id: int = 0
        self.active: bool = True
    
    def __repr__(self) -> str:
        return f"Context(id={self.context_id}, pc={self.pc:#x}, sp={self.sp:#x}, domain={self.domain_id})"


class TypeManager:
    """
    Type Manager
    
    Controls object creation and validation.
    Ensures objects are created with correct types
    and proper initialization.
    """
    
    def __init__(self, manager_id: int):
        self.manager_id = manager_id
        self.manages_types: List[ObjectType] = []
        self.created_objects: List[int] = []
    
    def can_create_type(self, obj_type: ObjectType) -> bool:
        """Check if this manager can create objects of given type"""
        return obj_type in self.manages_types
    
    def register_created_object(self, object_id: int):
        """Register an object created by this manager"""
        self.created_objects.append(object_id)
    
    def __repr__(self) -> str:
        types = [t.name for t in self.manages_types]
        return f"TypeManager(id={self.manager_id}, types={types})"


class ObjectTable:
    """
    Global Object Table
    
    Manages all objects in the system.
    In real iAPX 432, this would be in memory.
    """
    
    def __init__(self, memory: Memory):
        self.memory = memory
        self.objects: Dict[int, dict] = {}
        self.next_object_id: int = 1
        self.type_managers: Dict[int, TypeManager] = {}
        self.domains: Dict[int, Domain] = {}
        self.contexts: Dict[int, Context] = {}
    
    def create_object(self, obj_type: ObjectType, size: int = 4) -> int:
        """
        Create a new object
        
        Args:
            obj_type: Type of object to create
            size: Size in bytes (default: 4)
            
        Returns:
            Object ID
        """
        obj_id = self.next_object_id
        self.next_object_id += 1
        
        self.objects[obj_id] = {
            'type': obj_type,
            'size': size,
            'data': [0] * size,
            'initialized': True
        }
        
        return obj_id
    
    def get_object(self, object_id: int) -> Optional[dict]:
        """Get object by ID"""
        return self.objects.get(object_id)
    
    def delete_object(self, object_id: int) -> bool:
        """Delete object"""
        if object_id in self.objects:
            del self.objects[object_id]
            return True
        return False
    
    def create_domain(self, parent_domain_id: Optional[int] = None) -> int:
        """Create a new domain"""
        domain_id = self.next_object_id
        domain = Domain(domain_id)
        domain.parent_domain_id = parent_domain_id
        self.domains[domain_id] = domain
        
        # Register as child of parent
        if parent_domain_id and parent_domain_id in self.domains:
            self.domains[parent_domain_id].child_domain_ids.append(domain_id)
            domain.created_by = parent_domain_id
        
        return domain_id
    
    def create_context(self, domain_id: int) -> int:
        """Create a new context"""
        context_id = self.next_object_id
        context = Context(context_id)
        context.domain_id = domain_id
        self.contexts[context_id] = context
        
        return context_id
    
    def get_domain(self, domain_id: int) -> Optional[Domain]:
        """Get domain by ID"""
        return self.domains.get(domain_id)
    
    def get_context(self, context_id: int) -> Optional[Context]:
        """Get context by ID"""
        return self.contexts.get(context_id)
    
    def create_type_manager(self, manager_id: int, types: List[ObjectType]) -> TypeManager:
        """Create a type manager"""
        manager = TypeManager(manager_id)
        manager.manages_types = types
        self.type_managers[manager_id] = manager
        return manager
    
    def __repr__(self) -> str:
        return (f"ObjectTable(objects={len(self.objects)}, "
                f"domains={len(self.domains)}, "
                f"contexts={len(self.contexts)})")
