"""
Admin ranking calculation module using lambda formula.
Formula: lambda = cr50 + 1/cdt50 + r50 + 1/lr1m
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from data_fetcher import AdminDataFetcher


class AdminRanking:
    """Calculates admin rankings using lambda formula."""
    
    def __init__(self):
        """Initialize the ranking calculator."""
        self.data_fetcher = AdminDataFetcher()
        self.recent_calls_limit = 50
        self.recent_ratings_limit = 50
    
    def calculate_cr50(self, call_data: pd.DataFrame, admin_id: str) -> float:
        """
        Calculate cr50: average internal_rating for last 50 calls per admin.
        
        Args:
            call_data: DataFrame with call data
            admin_id: Admin UUID
            
        Returns:
            Average internal rating for last 50 calls
        """
        admin_calls = call_data[call_data['admin_id'] == admin_id].copy()
        
        if admin_calls.empty:
            return 0.0
        
        # Sort by created_at descending and take last 50
        admin_calls = admin_calls.sort_values('created_at', ascending=False).head(self.recent_calls_limit)
        
        # Filter out null internal_rating values
        valid_ratings = admin_calls['internal_rating'].dropna()
        
        if valid_ratings.empty:
            return 0.0
        
        return float(valid_ratings.mean())
    
    def calculate_cdt50(self, call_data: pd.DataFrame, admin_id: str) -> float:
        """
        Calculate 1/cdt50: inverse of average credentials_delivery_time for last 50 calls per admin.
        
        Args:
            call_data: DataFrame with call data  
            admin_id: Admin UUID
            
        Returns:
            Inverse of average credentials delivery time for last 50 calls
        """
        admin_calls = call_data[call_data['admin_id'] == admin_id].copy()
        
        if admin_calls.empty:
            return 0.0
        
        # Sort by created_at descending and take last 50
        admin_calls = admin_calls.sort_values('created_at', ascending=False).head(self.recent_calls_limit)
        
        # Filter out null credentials_delivery_time values
        valid_times = admin_calls['credentials_delivery_time'].dropna()
        
        if valid_times.empty or valid_times.mean() == 0:
            return 0.0
        
        avg_delivery_time = float(valid_times.mean())
        return 1.0 / avg_delivery_time if avg_delivery_time > 0 else 0.0
    
    def calculate_r50(self, rating_data: pd.DataFrame, admin_id: str) -> float:
        """
        Calculate r50: average chat rating for last 50 ratings per admin.
        
        Args:
            rating_data: DataFrame with chat rating data
            admin_id: Admin UUID (mapped to user_id in ratings table)
            
        Returns:
            Average chat rating for last 50 ratings
        """
        admin_ratings = rating_data[rating_data['user_id'] == admin_id].copy()
        
        if admin_ratings.empty:
            return 0.0
        
        # Sort by created_at descending and take last 50
        admin_ratings = admin_ratings.sort_values('created_at', ascending=False).head(self.recent_ratings_limit)
        
        # Filter out null rating values
        valid_ratings = admin_ratings['rating'].dropna()
        
        if valid_ratings.empty:
            return 0.0
        
        return float(valid_ratings.mean())
    
    def calculate_lr1m(self, leave_data: pd.DataFrame, admin_id: str) -> float:
        """
        Calculate 1/lr1m: inverse of leave requests count in last month per admin.
        
        Args:
            leave_data: DataFrame with leave request data
            admin_id: Admin UUID (mapped to user_id in leave data)
            
        Returns:
            Inverse of leave requests count in last month
        """
        if leave_data.empty or 'user_id' not in leave_data.columns:
            # No leave requests data at all
            return 1.0
        admin_leaves = leave_data[leave_data['user_id'] == admin_id].copy()
        if admin_leaves.empty:
            # No leave requests means high availability - return high score
            return 1.0
        leave_count = len(admin_leaves)
        # If no leaves, return 1.0 (high score)
        # If leaves exist, return inverse (more leaves = lower score)
        return 1.0 / (leave_count + 1) if leave_count > 0 else 1.0
    
    def calculate_lambda_score(self, call_data: pd.DataFrame, rating_data: pd.DataFrame, 
                              leave_data: pd.DataFrame, admin_id: str) -> Dict[str, float]:
        """
        Calculate complete lambda score for an admin.
        
        Args:
            call_data: DataFrame with call data
            rating_data: DataFrame with rating data  
            leave_data: DataFrame with leave data
            admin_id: Admin UUID
            
        Returns:
            Dictionary with component scores and final lambda score
        """
        cr50 = self.calculate_cr50(call_data, admin_id)
        cdt50_inverse = self.calculate_cdt50(call_data, admin_id)
        r50 = self.calculate_r50(rating_data, admin_id)
        lr1m_inverse = self.calculate_lr1m(leave_data, admin_id)
        
        lambda_score = cr50 + cdt50_inverse + r50 + lr1m_inverse
        
        return {
            'admin_id': admin_id,
            'cr50': cr50,
            'cdt50_inverse': cdt50_inverse,
            'r50': r50,
            'lr1m_inverse': lr1m_inverse,
            'lambda_score': lambda_score
        }
    
    def rank_all_admins(self) -> pd.DataFrame:
        """
        Calculate lambda scores for all admins and return ranked results.
        
        Returns:
            DataFrame with admin rankings sorted by lambda score (descending)
        """
        print("Fetching data from all tables...")
        
        # Fetch all data
        call_data = self.data_fetcher.get_all_call_data()
        rating_data = self.data_fetcher.get_all_chat_ratings()
        leave_data = self.data_fetcher.get_all_leave_requests()
        
        if call_data.empty:
            print("No call data available for ranking")
            return pd.DataFrame()
        
        # Get unique admin IDs from call data
        admin_ids = call_data['admin_id'].unique()
        print(f"Found {len(admin_ids)} unique admins")
        
        # Calculate lambda scores for each admin
        results = []
        for i, admin_id in enumerate(admin_ids, 1):
            print(f"Processing admin {i}/{len(admin_ids)}: {admin_id}")
            
            score_data = self.calculate_lambda_score(
                call_data, rating_data, leave_data, admin_id
            )
            
            # Get admin name from call data
            admin_name = call_data[call_data['admin_id'] == admin_id]['admin_name'].iloc[0] \
                        if not call_data[call_data['admin_id'] == admin_id].empty else 'Unknown'
            
            score_data['admin_name'] = admin_name
            results.append(score_data)
        
        # Create DataFrame and sort by lambda score
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('lambda_score', ascending=False).reset_index(drop=True)
        results_df['rank'] = results_df.index + 1
        
        return results_df
    
    def get_top_admins(self, top_n: int = 10) -> pd.DataFrame:
        """
        Get top N ranked admins.
        
        Args:
            top_n: Number of top admins to return
            
        Returns:
            DataFrame with top ranked admins
        """
        all_rankings = self.rank_all_admins()
        return all_rankings.head(top_n)
    
    def get_admin_detailed_analysis(self, admin_id: str) -> Dict:
        """
        Get detailed analysis for a specific admin.
        
        Args:
            admin_id: Admin UUID
            
        Returns:
            Dictionary with detailed metrics and recent records
        """
        print(f"Fetching detailed analysis for admin: {admin_id}")
        
        # Fetch all data
        call_data = self.data_fetcher.get_all_call_data()
        rating_data = self.data_fetcher.get_all_chat_ratings()
        leave_data = self.data_fetcher.get_all_leave_requests()
        
        # Calculate lambda score
        lambda_data = self.calculate_lambda_score(call_data, rating_data, leave_data, admin_id)
        
        # Get recent records for analysis
        admin_calls = call_data[call_data['admin_id'] == admin_id].sort_values('created_at', ascending=False).head(50)
        admin_ratings = rating_data[rating_data['user_id'] == admin_id].sort_values('created_at', ascending=False).head(50)
        if leave_data.empty or 'user_id' not in leave_data.columns:
            admin_leaves = pd.DataFrame()
        else:
            admin_leaves = leave_data[leave_data['user_id'] == admin_id].sort_values('created_at', ascending=False)
        
        return {
            'lambda_metrics': lambda_data,
            'recent_calls': admin_calls.to_dict('records'),
            'recent_ratings': admin_ratings.to_dict('records'),
            'recent_leaves': admin_leaves.to_dict('records'),
            'statistics': {
                'total_calls': len(admin_calls),
                'total_ratings': len(admin_ratings),  
                'total_leaves': len(admin_leaves),
                'avg_call_rating': admin_calls['internal_rating'].mean() if not admin_calls.empty else 0,
                'avg_delivery_time': admin_calls['credentials_delivery_time'].mean() if not admin_calls.empty else 0,
                'avg_chat_rating': admin_ratings['rating'].mean() if not admin_ratings.empty else 0
            }
        }