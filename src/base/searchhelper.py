from typing import List, Optional, Dict

from .mapping import Mapping


class SearchHelperMixin:
    """
    SearchHelperMixin provides possibility to get mapping and search helpers for user-friendly search API
    """

    fields_to_exclude_from_mapping: Optional[List[str]] = None
    fields_to_exclude_from_suggestions: Optional[List[str]] = None

    _mapping_class = None

    _full_mapping: Optional[Mapping] = None
    _raw_mapping = None

    @classmethod
    def get_mapping(cls) -> List[str]:
        """
        Returns full mapping with handwritten fields in search set class and their sources
        Except of excluded fields/sources
        """
        return list(cls.get_full_mapping().keys())

    @classmethod
    def get_mapping_to_suggestion(cls) -> Dict[str, bool]:
        return {k: v.show_suggestions for k, v in cls.get_full_mapping().items()}

    @classmethod
    def get_fields_values(cls, field_name, prefix='') -> List[str]:
        """
        Returns search helpers for field by prefix
        """
        return cls.get_full_mapping().get_values(field_name=field_name, prefix=prefix)

    @classmethod
    def get_fields_to_exclude_from_mapping(cls) -> List[str]:
        return cls.fields_to_exclude_from_mapping if cls.fields_to_exclude_from_mapping is not None else list()

    @classmethod
    def get_fields_to_exclude_from_suggestions(cls) -> List[str]:
        return cls.fields_to_exclude_from_suggestions if cls.fields_to_exclude_from_suggestions is not None else list()

    @classmethod
    def get_raw_mapping(cls) -> List[str]:
        """
        Caches raw mapping and return it
        """
        if cls._raw_mapping is None:
            cls._raw_mapping = cls._get_raw_mapping()
        return cls._raw_mapping

    @classmethod
    def get_full_mapping(cls):
        if cls._full_mapping is None:
            cls._fill_mapping()
        return cls._full_mapping

    @classmethod
    def _fill_mapping(cls):
        """
        Fill mapping extended by handwritten fields and its sources
        """

        fields_to_exclude_from_mapping = cls.get_fields_to_exclude_from_mapping()
        fields_to_exclude_from_suggestions = cls.get_fields_to_exclude_from_suggestions()

        mapping = cls._mapping_class(cls.Meta.model)

        # create mapping values from fields in searchset class
        for field_name, field in cls.get_field_name_to_field().items():
            if field_name not in fields_to_exclude_from_mapping:
                mapping.add_value(name=field_name,
                                  sources=field.sources,
                                  get_available_values_method=field.get_available_values_method,
                                  show_suggestions=(field.show_suggestions
                                                    and field_name not in fields_to_exclude_from_suggestions))

            if not field.exclude_sources_from_mapping:
                for source in field.sources:
                    mapping.add_value(name=source,
                                      get_available_values_method=field.get_available_values_method,
                                      show_suggestions=source not in fields_to_exclude_from_suggestions)

        # update mapping from mapping in database/elastic/etc
        raw_mapping = cls.get_raw_mapping()

        for name in raw_mapping:
            if name not in fields_to_exclude_from_mapping:
                mapping.add_value(name=name,
                                  show_suggestions=name not in fields_to_exclude_from_suggestions)

        cls._full_mapping = mapping

    @classmethod
    def _get_raw_mapping(cls) -> List[str]:
        """
        That method allows to get mapping in raw format. It have to be reimplemented
        """
        raise NotImplementedError()
