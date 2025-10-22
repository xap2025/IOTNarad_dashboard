"""
OEE Calculation Service
Handles Overall Equipment Effectiveness calculations and manufacturing metrics
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class OEEStatus(Enum):
    """OEE performance status levels"""
    EXCELLENT = "excellent"  # >= 90%
    GOOD = "good"          # 80-89%
    FAIR = "fair"          # 70-79%
    POOR = "poor"          # < 70%


@dataclass
class OEEData:
    """OEE data structure"""
    line_id: str
    line_name: str
    timestamp: datetime
    
    # OEE Components
    availability: float
    performance: float
    quality: float
    overall_oee: float
    
    # Production Data
    planned_production_time: float  # minutes
    actual_production_time: float   # minutes
    ideal_cycle_time: float        # minutes per unit
    actual_cycle_time: float       # minutes per unit
    total_units_produced: int
    good_units_produced: int
    defective_units: int
    
    # Downtime Data
    equipment_failure_time: float   # minutes
    setup_adjustment_time: float    # minutes
    idling_minor_stops_time: float  # minutes
    startup_reject_time: float      # minutes
    
    # Losses
    reduced_speed_loss: float       # percentage
    production_rejects: float       # percentage


class OEEService:
    """
    OEE Calculation Service
    Handles all OEE-related calculations and manufacturing metrics
    """
    
    def __init__(self):
        self.target_oee = float(os.getenv('TARGET_OEE', 85.0))
        self.target_availability = float(os.getenv('TARGET_AVAILABILITY', 90.0))
        self.target_performance = float(os.getenv('TARGET_PERFORMANCE', 95.0))
        self.target_quality = float(os.getenv('TARGET_QUALITY', 99.0))
        
        logger.info("OEE Service initialized")
        logger.info(f"Target OEE: {self.target_oee}%")
    
    def calculate_oee(self, oee_data: OEEData) -> Dict[str, Any]:
        """
        Calculate comprehensive OEE metrics
        
        Args:
            oee_data: OEEData object with production information
            
        Returns:
            Dictionary with calculated OEE metrics
        """
        try:
            # Calculate Availability
            availability = self._calculate_availability(oee_data)
            
            # Calculate Performance
            performance = self._calculate_performance(oee_data)
            
            # Calculate Quality
            quality = self._calculate_quality(oee_data)
            
            # Calculate Overall OEE
            overall_oee = availability * performance * quality / 10000
            
            # Calculate Six Big Losses
            six_big_losses = self._calculate_six_big_losses(oee_data)
            
            # Determine status
            oee_status = self._get_oee_status(overall_oee)
            availability_status = self._get_oee_status(availability)
            performance_status = self._get_oee_status(performance)
            quality_status = self._get_oee_status(quality)
            
            result = {
                'line_id': oee_data.line_id,
                'line_name': oee_data.line_name,
                'timestamp': oee_data.timestamp.isoformat(),
                
                # OEE Scores
                'overall_oee': round(overall_oee, 2),
                'availability': round(availability, 2),
                'performance': round(performance, 2),
                'quality': round(quality, 2),
                
                # Status
                'oee_status': oee_status.value,
                'availability_status': availability_status.value,
                'performance_status': performance_status.value,
                'quality_status': quality_status.value,
                
                # Production Metrics
                'total_units_produced': oee_data.total_units_produced,
                'good_units_produced': oee_data.good_units_produced,
                'defective_units': oee_data.defective_units,
                'production_rate': self._calculate_production_rate(oee_data),
                
                # Time Metrics
                'planned_production_time': oee_data.planned_production_time,
                'actual_production_time': oee_data.actual_production_time,
                'uptime_percentage': round((oee_data.actual_production_time / oee_data.planned_production_time) * 100, 2),
                
                # Cycle Time Metrics
                'ideal_cycle_time': oee_data.ideal_cycle_time,
                'actual_cycle_time': oee_data.actual_cycle_time,
                'cycle_time_efficiency': round((oee_data.ideal_cycle_time / oee_data.actual_cycle_time) * 100, 2),
                
                # Six Big Losses
                'six_big_losses': six_big_losses,
                
                # Overall Loss Percentage
                'total_loss_percentage': round(100 - overall_oee, 2),
                
                # Targets vs Actual
                'oee_vs_target': round(overall_oee - self.target_oee, 2),
                'availability_vs_target': round(availability - self.target_oee, 2),
                'performance_vs_target': round(performance - self.target_performance, 2),
                'quality_vs_target': round(quality - self.target_quality, 2),
            }
            
            logger.debug(f"OEE calculated for {oee_data.line_id}: {overall_oee:.2f}%")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating OEE for {oee_data.line_id}: {e}")
            return {}
    
    def _calculate_availability(self, oee_data: OEEData) -> float:
        """
        Calculate Availability = (Actual Production Time / Planned Production Time) * 100
        """
        if oee_data.planned_production_time == 0:
            return 0.0
        
        availability = (oee_data.actual_production_time / oee_data.planned_production_time) * 100
        return min(100.0, max(0.0, availability))
    
    def _calculate_performance(self, oee_data: OEEData) -> float:
        """
        Calculate Performance = (Ideal Cycle Time / Actual Cycle Time) * 100
        """
        if oee_data.actual_cycle_time == 0:
            return 0.0
        
        performance = (oee_data.ideal_cycle_time / oee_data.actual_cycle_time) * 100
        return min(100.0, max(0.0, performance))
    
    def _calculate_quality(self, oee_data: OEEData) -> float:
        """
        Calculate Quality = (Good Units Produced / Total Units Produced) * 100
        """
        if oee_data.total_units_produced == 0:
            return 0.0
        
        quality = (oee_data.good_units_produced / oee_data.total_units_produced) * 100
        return min(100.0, max(0.0, quality))
    
    def _calculate_six_big_losses(self, oee_data: OEEData) -> Dict[str, float]:
        """
        Calculate the Six Big Losses in manufacturing
        """
        planned_time = oee_data.planned_production_time
        
        if planned_time == 0:
            return {
                'equipment_failure': 0.0,
                'setup_adjustments': 0.0,
                'idling_minor_stops': 0.0,
                'reduced_speed': 0.0,
                'startup_rejects': 0.0,
                'production_rejects': 0.0
            }
        
        # Time-based losses (as percentage of planned time)
        equipment_failure = (oee_data.equipment_failure_time / planned_time) * 100
        setup_adjustments = (oee_data.setup_adjustment_time / planned_time) * 100
        idling_minor_stops = (oee_data.idling_minor_stops_time / planned_time) * 100
        startup_rejects = (oee_data.startup_reject_time / planned_time) * 100
        
        # Performance and quality losses
        reduced_speed = oee_data.reduced_speed_loss
        production_rejects = oee_data.production_rejects
        
        return {
            'equipment_failure': round(equipment_failure, 2),
            'setup_adjustments': round(setup_adjustments, 2),
            'idling_minor_stops': round(idling_minor_stops, 2),
            'reduced_speed': round(reduced_speed, 2),
            'startup_rejects': round(startup_rejects, 2),
            'production_rejects': round(production_rejects, 2)
        }
    
    def _calculate_production_rate(self, oee_data: OEEData) -> float:
        """Calculate production rate (units per hour)"""
        if oee_data.actual_production_time == 0:
            return 0.0
        
        return (oee_data.total_units_produced / oee_data.actual_production_time) * 60
    
    def _get_oee_status(self, value: float) -> OEEStatus:
        """Determine OEE status based on value"""
        if value >= 90:
            return OEEStatus.EXCELLENT
        elif value >= 80:
            return OEEStatus.GOOD
        elif value >= 70:
            return OEEStatus.FAIR
        else:
            return OEEStatus.POOR
    
    def calculate_shift_oee(self, line_id: str, shift_start: datetime, shift_end: datetime) -> Dict[str, Any]:
        """
        Calculate OEE for a specific shift
        
        Args:
            line_id: Production line identifier
            shift_start: Shift start time
            shift_end: Shift end time
            
        Returns:
            Dictionary with shift OEE metrics
        """
        try:
            # This would typically query your database for shift data
            # For now, we'll create a sample calculation
            
            shift_duration = (shift_end - shift_start).total_seconds() / 60  # minutes
            
            # Sample shift data (in production, this would come from your database)
            sample_data = OEEData(
                line_id=line_id,
                line_name=f"Line {line_id}",
                timestamp=shift_end,
                
                # Time data (minutes)
                planned_production_time=shift_duration - 30,  # 30 min break
                actual_production_time=shift_duration - 60,   # 60 min downtime
                ideal_cycle_time=2.0,                        # 2 min per unit
                actual_cycle_time=2.3,                       # 2.3 min per unit
                
                # Production data
                total_units_produced=450,
                good_units_produced=435,
                defective_units=15,
                
                # Downtime data
                equipment_failure_time=25.0,
                setup_adjustment_time=15.0,
                idling_minor_stops_time=20.0,
                startup_reject_time=5.0,
                
                # Loss percentages
                reduced_speed_loss=3.2,
                production_rejects=3.3
            )
            
            return self.calculate_oee(sample_data)
            
        except Exception as e:
            logger.error(f"Error calculating shift OEE for {line_id}: {e}")
            return {}
    
    def get_oee_trends(self, line_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get OEE trends for a production line over specified days
        
        Args:
            line_id: Production line identifier
            days: Number of days to retrieve trends for
            
        Returns:
            List of OEE data points
        """
        try:
            trends = []
            end_date = datetime.now()
            
            for i in range(days):
                date = end_date - timedelta(days=i)
                
                # Generate sample trend data (in production, query your database)
                trend_data = {
                    'date': date.strftime('%Y-%m-%d'),
                    'overall_oee': 85 + (i % 3) * 2 + (i % 2) * (-1),
                    'availability': 90 + (i % 4) * 1.5,
                    'performance': 88 + (i % 3) * 2.5,
                    'quality': 92 + (i % 2) * 1.8,
                    'total_units': 450 + (i % 5) * 25,
                    'good_units': 435 + (i % 5) * 20,
                    'downtime_minutes': 45 + (i % 3) * 10
                }
                
                trends.append(trend_data)
            
            return sorted(trends, key=lambda x: x['date'])
            
        except Exception as e:
            logger.error(f"Error getting OEE trends for {line_id}: {e}")
            return []
    
    def calculate_plant_oee(self, lines_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall plant OEE from multiple production lines
        
        Args:
            lines_data: List of OEE data from individual lines
            
        Returns:
            Dictionary with plant-level OEE metrics
        """
        try:
            if not lines_data:
                return {}
            
            # Calculate weighted averages based on production volume
            total_units = sum(line.get('total_units_produced', 0) for line in lines_data)
            
            if total_units == 0:
                return {}
            
            # Weighted OEE calculation
            weighted_oee = sum(
                line.get('overall_oee', 0) * line.get('total_units_produced', 0) 
                for line in lines_data
            ) / total_units
            
            weighted_availability = sum(
                line.get('availability', 0) * line.get('total_units_produced', 0) 
                for line in lines_data
            ) / total_units
            
            weighted_performance = sum(
                line.get('performance', 0) * line.get('total_units_produced', 0) 
                for line in lines_data
            ) / total_units
            
            weighted_quality = sum(
                line.get('quality', 0) * line.get('total_units_produced', 0) 
                for line in lines_data
            ) / total_units
            
            return {
                'plant_oee': round(weighted_oee, 2),
                'plant_availability': round(weighted_availability, 2),
                'plant_performance': round(weighted_performance, 2),
                'plant_quality': round(weighted_quality, 2),
                'total_units_produced': total_units,
                'total_good_units': sum(line.get('good_units_produced', 0) for line in lines_data),
                'total_defective_units': sum(line.get('defective_units', 0) for line in lines_data),
                'active_lines': len([line for line in lines_data if line.get('oee_status') != 'poor']),
                'total_lines': len(lines_data),
                'plant_status': self._get_oee_status(weighted_oee).value
            }
            
        except Exception as e:
            logger.error(f"Error calculating plant OEE: {e}")
            return {}
    
    def get_oee_benchmarks(self) -> Dict[str, float]:
        """
        Get industry benchmarks for OEE metrics
        
        Returns:
            Dictionary with benchmark values
        """
        return {
            'world_class_oee': 85.0,
            'excellent_oee': 80.0,
            'good_oee': 70.0,
            'average_oee': 60.0,
            'poor_oee': 50.0,
            
            'world_class_availability': 95.0,
            'world_class_performance': 95.0,
            'world_class_quality': 99.0,
            
            'target_oee': self.target_oee,
            'target_availability': self.target_availability,
            'target_performance': self.target_performance,
            'target_quality': self.target_quality
        }
    
    def generate_oee_report(self, line_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate comprehensive OEE report for a production line
        
        Args:
            line_id: Production line identifier
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Dictionary with comprehensive OEE report
        """
        try:
            # Get trends data
            days = (end_date - start_date).days + 1
            trends = self.get_oee_trends(line_id, days)
            
            if not trends:
                return {}
            
            # Calculate averages
            avg_oee = sum(trend['overall_oee'] for trend in trends) / len(trends)
            avg_availability = sum(trend['availability'] for trend in trends) / len(trends)
            avg_performance = sum(trend['performance'] for trend in trends) / len(trends)
            avg_quality = sum(trend['quality'] for trend in trends) / len(trends)
            
            # Calculate totals
            total_units = sum(trend['total_units'] for trend in trends)
            total_good_units = sum(trend['good_units'] for trend in trends)
            total_downtime = sum(trend['downtime_minutes'] for trend in trends)
            
            return {
                'line_id': line_id,
                'report_period': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'days': days
                },
                'averages': {
                    'oee': round(avg_oee, 2),
                    'availability': round(avg_availability, 2),
                    'performance': round(avg_performance, 2),
                    'quality': round(avg_quality, 2)
                },
                'totals': {
                    'units_produced': total_units,
                    'good_units': total_good_units,
                    'defective_units': total_units - total_good_units,
                    'downtime_hours': round(total_downtime / 60, 2)
                },
                'trends': trends,
                'benchmarks': self.get_oee_benchmarks(),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating OEE report for {line_id}: {e}")
            return {}
