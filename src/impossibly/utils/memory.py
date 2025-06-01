'''
A data structure to track global memory of all Agents within a Graph. Stores each prompt/response as JSON objects, able to be queried upon and filtered.
'''

from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, List

from impossibly.utils.start_end import END

if TYPE_CHECKING:
    from impossibly import Agent  # Import only for type checking


class Memory:
    def __init__(self):
        self.memory = []

    def add(self, author: 'Agent', recipient: 'Agent', content: str):
        """
        Public method that transparently handles both sync and async execution.
        
        This method detects if it's being called from an async context and acts accordingly.
        If called from sync code, it runs the async implementation using asyncio.run().
        If called from async code, it returns a coroutine that can be awaited.
        """
        try:
            # Check if we're in an event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're being called from an async context
                # Return the coroutine for the caller to await
                return self._add_async(author, recipient, content)
            else:
                # No running event loop, create one
                return asyncio.run(self._add_async(author, recipient, content))
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(self._add_async(author, recipient, content))
    
    async def _add_async(self, author: 'Agent', recipient: 'Agent', content: str):
        """Internal async implementation of add."""
        if recipient is END:
            recipient.name = 'END'
        new = {
            'author': author.name,
            'recipient': recipient.name,
            'content': content
        }
        self.memory.append(new)
    
    def get(self, author: List['Agent'], recipient: List['Agent']):
        """
        Public method that transparently handles both sync and async execution.
        
        This method detects if it's being called from an async context and acts accordingly.
        If called from sync code, it runs the async implementation using asyncio.run().
        If called from async code, it returns a coroutine that can be awaited.
        """
        try:
            # Check if we're in an event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're being called from an async context
                # Return the coroutine for the caller to await
                return self._get_async(author, recipient)
            else:
                # No running event loop, create one
                return asyncio.run(self._get_async(author, recipient))
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(self._get_async(author, recipient))
    
    async def _get_async(self, author: List['Agent'], recipient: List['Agent']):
        """Internal async implementation of get."""
        return [m for m in self.memory if m['author'] in author and m['recipient'] in recipient]
    
    def get_formatted(self, author: List['Agent'], recipient: List['Agent']):
        """
        Public method that transparently handles both sync and async execution.
        
        This method detects if it's being called from an async context and acts accordingly.
        If called from sync code, it runs the async implementation using asyncio.run().
        If called from async code, it returns a coroutine that can be awaited.
        """
        try:
            # Check if we're in an event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're being called from an async context
                # Return the coroutine for the caller to await
                return self._get_formatted_async(author, recipient)
            else:
                # No running event loop, create one
                return asyncio.run(self._get_formatted_async(author, recipient))
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(self._get_formatted_async(author, recipient))
    
    async def _get_formatted_async(self, author: List['Agent'], recipient: List['Agent']):
        '''
        Internal async implementation to format messages between specified authors and recipients.
        '''
        return '\n'.join([f"{m['author']} -> {m['recipient']}: {m['content']}" for m in self.memory if m['author'] in [a.name for a in author] and m['recipient'] in [a.name for a in recipient]])

    def get_all(self):
        """
        Public method that transparently handles both sync and async execution.
        
        This method detects if it's being called from an async context and acts accordingly.
        If called from sync code, it runs the async implementation using asyncio.run().
        If called from async code, it returns a coroutine that can be awaited.
        """
        try:
            # Check if we're in an event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're being called from an async context
                # Return the coroutine for the caller to await
                return self._get_all_async()
            else:
                # No running event loop, create one
                return asyncio.run(self._get_all_async())
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(self._get_all_async())
    
    async def _get_all_async(self):
        """Internal async implementation of get_all."""
        return self.memory

    def clear(self):
        """
        Public method that transparently handles both sync and async execution.
        
        This method detects if it's being called from an async context and acts accordingly.
        If called from sync code, it runs the async implementation using asyncio.run().
        If called from async code, it returns a coroutine that can be awaited.
        """
        try:
            # Check if we're in an event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're being called from an async context
                # Return the coroutine for the caller to await
                return self._clear_async()
            else:
                # No running event loop, create one
                return asyncio.run(self._clear_async())
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(self._clear_async())
    
    async def _clear_async(self):
        """Internal async implementation of clear."""
        self.memory = []

    def __str__(self):
        return str(self.memory)

    def __repr__(self):
        return str(self.memory)