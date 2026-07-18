import json
from copy import copy
from typing import Union

from ..utils import startup


class AbstractStoreItem:
    """Abstract class for Item

    Attributes
    ----------

    namespace: str
        The name of the namespace it belongs to

    """

    namespace: str = ""

    def __init__(self, id: str) -> None:
        """Item

        Parameters
        ----------
        id: str
            the id of the item
        """
        self.id = id

    def export(self, filepath: str):
        """Export the item into json file

        Parameters
        ----------
        filepath: str
            Path to where the Item should be exported
        """
        file = open(filepath, "w")
        data = self.get_dict()
        json.dump(data, file, indent=4)
        file.close()

    def get_dict(self) -> dict:
        """Returns dictionary representation of the Item

        Returns
        --------
        dict

        """
        raise NotImplementedError


class AbstractNamespace:
    """Abstract class for Namespace"""

    def __init__(self, filepath: str, namespace: str) -> None:
        """Namespace"""
        self._item_index: dict[str, AbstractStoreItem] = {}
        self.changes = False
        self.filepath = filepath
        self.namespace = namespace
        self.load(self.filepath)

    def get_by_id(self, item_id: str) -> Union[AbstractStoreItem, None]:
        """Get an item by it's ID

        Parameters
        ----------
        item_id: str
            The id of the item

        Returns
        -------
        Item or None
        """
        item = self._item_index.get(item_id)
        if item:
            return copy(item)
        return None

    def get_by_name(self, item_name: str) -> list[AbstractStoreItem]:
        """Gets all the items with the given name

        Parameters
        ----------
        item_name: str
            The name of the item

        Returns
        -------
        list
            Returns a list of Items
        """
        items = [
            copy(item) for item in self._item_index.values() if item.name == item_name
        ]
        return items

    def add(self, item: AbstractStoreItem):
        """Add a new item in the namespace

        Parameters
        ----------
        item: Item
            the item to be added

        Returns
        -------
        None
        """
        self._item_index[item.id] = item
        item.namespace = self.namespace
        self.changes = True
        self.store()

    def remove(self, item_id: str):
        """Remove an item

        Parameters
        ----------
        item_id: str
            the id if the item

        Returns
        --------
        None

        """
        del self._item_index[item_id]
        self.changes = True

    def load(self, filepath: str):
        """Load the namespace

        Parameters
        ----------
        filepath: str
            The path to where the namespace json file is located

        Returns
        --------
        None
        """
        raise NotImplementedError

    def store(self):
        """Save the namespace to it's filepath as a json file"""
        raise NotImplementedError

    def verify_namespace(self, data: dict) -> bool:
        """Check if the loaded namespace is valid or not.

        Parameters
        -----------
        data: dict
            The data of the namespace

        Returns
        --------
        bool
        """
        raise NotImplementedError


class AbstractStore:
    """Abstract class for stores

    Attributes
    ----------
    namespace: dict[str, Namespace]
        Contains all the namespaces of the Items

    _item_index: dict[str, Item]
        Contains all the Items

    """

    namespace: dict[str, AbstractNamespace] = {}
    _item_index: dict[str, AbstractStoreItem] = {}

    def __init__(self) -> None:
        """Store"""
        startup.add_callback(self._load_user_namespace)

    def get_all(self):
        """Get all items of the store

        Returns
        -------
        list
        """
        return self._item_index.values()

    def get_by_id(self, item_id: str):
        """
        Gets an item by it's id

        Parameters
        ----------
        item_id: str

        Returns
        -------
        Item or None
            Returns the item if found or None
        """
        item = self._item_index.get(item_id)
        if item:
            return copy(item)
        return None

    def get_by_name(self, item_name: str) -> list[AbstractStoreItem]:
        """Gets all the items with the given name

        Parameters
        ----------
        item_name: str
            The name of the item

        Returns
        -------
        list[Item]
            Returns a list of Items
        """
        items = [
            copy(item) for item in self._item_index.values() if item.name == item_name
        ]
        return items

    def add(self, namespace: str, item: AbstractStoreItem):
        """Add a new item in a namespace

        Parameters
        ----------
        namespace: str
            the name of the namespace where the item should be added
        item: Item
            the item to be added

        Returns
        -------
        None
        """
        item_namespace = self.namespace.get(namespace)
        if item_namespace:
            item_namespace.add(item)
            self._item_index[item.id] = item
        else:
            print(f"Gscatter: Namespace: {namespace} not found.")

    def remove(self, item_id: str):
        """Remove an item

        Parameters
        ----------
        item_id: str
            the id if the item

        Returns
        --------
        None

        """
        item = self._item_index.get(item_id)
        if item:
            namespace = self.namespace.get(item.namespace)
            if namespace:
                namespace.remove(item_id)
            del self._item_index[item_id]

    def update(self, item: AbstractStoreItem):
        """Update an item

        Parameters
        ----------
        item: AbstractStoreItem

        Returns
        ------
        None

        """
        raise NotImplementedError

    def load(self, filepath: str, namespace: str):
        """Load a namespace

        Parameters
        ----------
        filepath: str
            The path to where the namespace json file is located

        namespace: str
            The name of the namespace

        Returns
        --------
        None
        """
        raise NotImplementedError

    def merge(self, filepath: str, namespace: str):
        """Merge a namespace into already existing namespace"""
        raise NotImplementedError

    def _load_user_namespace(self):
        """Load user namespace"""
        raise NotImplementedError

    def unload(self, namespace: str):
        """Unload a namespace

        Parameters
        -----------
        namespace: str
            The name of the namespace to unload

        Returns
        ---------
        None
        """
        item_namespace = self.namespace.get(namespace)

        if item_namespace:
            for item in item_namespace._item_index:
                del self._item_index[item]
            del self.namespace[namespace]

    def store(self):
        """Save all the namespaces to it's respective filepaths"""
        for namespace in self.namespace.values():
            namespace.store()
