from collections import deque
from typing import TypeVar, Generic, Optional, List

T = TypeVar('T')

class Cola(Generic[T]):
    """
    Implementación de un TDA Cola (FIFO) para gestionar misiones en RPG.
    """
    def __init__(self):
        self._items = deque()
    
    def enqueue(self, item: T) -> None:
        """Añade una misión al final de la cola"""
        self._items.append(item)
    
    def dequeue(self) -> Optional[T]:
        """Elimina y retorna la primera misión de la cola"""
        if self.is_empty():
            return None
        return self._items.popleft()
    
    def first(self) -> Optional[T]:
        """Retorna la primera misión sin removerla"""
        if self.is_empty():
            return None
        return self._items[0]
    
    def is_empty(self) -> bool:
        """Verifica si la cola está vacía"""
        return len(self._items) == 0
    
    def size(self) -> int:
        """Retorna la cantidad de misiones en la cola"""
        return len(self._items)
    
    def to_list(self) -> List[T]:
        """Convierte la cola a una lista (para serialización)"""
        return list(self._items)
    
    def __iter__(self):
        """Permite iterar sobre los elementos de la cola"""
        return iter(self._items)