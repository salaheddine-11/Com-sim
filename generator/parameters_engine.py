# -*- coding: utf-8 -*-
"""
Effective-Dated Parameter Resolution Engine for Souss Agri-Pack SARL.
Loads config/parameters.yaml and dynamically resolves any fiscal, social, customs,
or banking parameter at any specific historical simulation date.
"""

from datetime import date
from decimal import Decimal
from typing import Dict, Any, List, Optional
import yaml
import os


class ParameterEngine:
    def __init__(self, parameters_yaml_path: str):
        self.parameters_path = parameters_yaml_path
        self.parameter_entries: List[Dict[str, Any]] = []
        self._load_parameters()

    def _load_parameters(self):
        with open(self.parameters_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        self.parameter_entries = data.get("parameters", [])

    def get_value(self, key_query: str, as_of_date: date) -> Any:
        date_str = as_of_date.isoformat()
        q = key_query.lower()

        # 1. Exact match on parameter_name with date range
        for p in self.parameter_entries:
            pname = p.get("parameter_name", "").lower()
            start = p.get("valid_from", "1900-01-01")
            end = p.get("valid_to", "2099-12-31")
            if (pname == q or pname.startswith(q)) and (start <= date_str <= end):
                return p.get("value")

        # 2. Fuzzy / Keyword alias match
        alias_map = {
            "tva_standard": ["tva_rate_standard", "tva_taux_normal"],
            "tva_electricity_mv": ["tva_rate_electricity_mt_onee", "tva_electricite"],
            "tva_water_industrial": ["tva_rate_water_industrial", "tva_eau"],
            "bam_key_rate": ["bam_key_rate", "bank_al_maghrib_key_rate", "taux_directeur_bam"],
            "taxe_professionnelle_rate": ["taxe_professionnelle_industrial_rate", "taxe_professionnelle"],
            "taxe_services_communaux_rate": ["taxe_services_communaux_urban_rate", "taxe_services_communaux"],
            "customs_tpi_rate": ["taxe_parafiscale_importation_tpi_rate", "tpi_rate", "tpi"],
            "cotisation_minimale_rate": ["cotisation_minimale_rate", "cotisation_minimale"],
            "cotisation_minimale_floor_mad": ["cotisation_minimale_minimum_floor_mad", "cotisation_minimale_floor"]
        }

        aliases = alias_map.get(q, [q])
        for alias in aliases:
            for p in self.parameter_entries:
                pname = p.get("parameter_name", "").lower()
                start = p.get("valid_from", "1900-01-01")
                end = p.get("valid_to", "2099-12-31")
                if alias in pname and (start <= date_str <= end):
                    return p.get("value")

        # If not found, check if it's a fixed known constant in the schema
        defaults = {
            "tva_standard": 0.20,
            "tva_electricity_mv": 0.18 if as_of_date.year == 2025 else 0.20,
            "tva_water_industrial": 0.09 if as_of_date.year == 2025 else 0.10,
            "bam_key_rate": 0.0225,
            "taxe_professionnelle_rate": 0.10,
            "taxe_services_communaux_rate": 0.105,
            "customs_tpi_rate": 0.0025,
            "cotisation_minimale_rate": 0.0025,
            "cotisation_minimale_floor_mad": 3000.00
        }
        if q in defaults:
            return defaults[q]

        raise KeyError(f"Parameter '{key_query}' not found in parameters.yaml for date {date_str}")

    def get_decimal(self, key_query: str, as_of_date: date) -> Decimal:
        val = self.get_value(key_query, as_of_date)
        return Decimal(str(val))
