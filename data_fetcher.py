"""
Data fetcher module for retrieving data from Hasura GraphQL endpoint.
"""
import requests
import pandas as pd
from typing import Dict, List, Optional, Any
from config import (
    HASURA_ENDPOINT, HASURA_ADMIN_SECRET,
    ALL_ADMINS_CALL_DATA_QUERY, ALL_CHAT_RATINGS_QUERY, ALL_LEAVE_REQUESTS_QUERY,
    CALL_DATA_QUERY, CHAT_RATINGS_QUERY, LEAVE_REQUESTS_QUERY
)


class HasuraClient:
    """Client for interacting with Hasura GraphQL API."""
    
    def __init__(self):
        """Initialize the Hasura client."""
        self.endpoint = HASURA_ENDPOINT
        self.headers = {
            'Content-Type': 'application/json',
            'x-hasura-admin-secret': HASURA_ADMIN_SECRET
        }
        
        if not self.endpoint or not HASURA_ADMIN_SECRET:
            raise ValueError("Missing Hasura endpoint or admin secret in environment variables")
    
    def execute_query(self, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query against Hasura.
        
        Args:
            query: GraphQL query string
            variables: Query variables
            
        Returns:
            Query response data
            
        Raises:
            Exception: If query fails
        """
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            
            data = response.json()
            if 'errors' in data:
                raise Exception(f"GraphQL errors: {data['errors']}")
                
            return data['data']
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")


class AdminDataFetcher:
    """Fetches and processes admin-related data."""
    
    def __init__(self):
        """Initialize the data fetcher."""
        self.client = HasuraClient()
    
    def get_all_call_data(self, limit: int = 1000) -> pd.DataFrame:
        """
        Fetch all call data from whatsub_delivery_time table.
        
        Args:
            limit: Maximum number of records to fetch
            
        Returns:
            DataFrame with call data
        """
        try:
            variables = {'limit': limit}
            data = self.client.execute_query(ALL_ADMINS_CALL_DATA_QUERY, variables)
            
            if not data.get('whatsub_delivery_time'):
                print("No call data found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['whatsub_delivery_time'])
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # Filter out records with null admin_id
            df = df[df['admin_id'].notna()]
            
            print(f"Fetched {len(df)} call records")
            return df
            
        except Exception as e:
            print(f"Error fetching call data: {str(e)}")
            return pd.DataFrame()
    
    def get_all_chat_ratings(self, limit: int = 1000) -> pd.DataFrame:
        """
        Fetch all chat ratings from whatsub_admin_ratings table.
        
        Args:
            limit: Maximum number of records to fetch
        
        Returns:
            DataFrame with chat ratings
        """
        try:
            variables = {'limit': limit}
            data = self.client.execute_query(ALL_CHAT_RATINGS_QUERY, variables)
            
            if not data.get('whatsub_admin_ratings'):
                print("No chat ratings found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['whatsub_admin_ratings'])
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # Filter out records with null user_id
            df = df[df['user_id'].notna()]
            
            print(f"Fetched {len(df)} chat rating records")
            return df
            
        except Exception as e:
            print(f"Error fetching chat ratings: {str(e)}")
            return pd.DataFrame()
    
    def get_all_leave_requests(self) -> pd.DataFrame:
        """
        Fetch all leave requests from whatsub_room_user_mapping table.
        
        Returns:
            DataFrame with leave requests
        """
        try:
            data = self.client.execute_query(ALL_LEAVE_REQUESTS_QUERY)
            
            if not data.get('whatsub_room_user_mapping'):
                print("No leave requests found")
                return pd.DataFrame()
            
            df = pd.DataFrame(data['whatsub_room_user_mapping'])
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            print(f"Fetched {len(df)} leave request records")
            return df
            
        except Exception as e:
            print(f"Error fetching leave requests: {str(e)}")
            return pd.DataFrame()
    
    def get_admin_specific_data(self, admin_id: str, limit: int = 50) -> Dict[str, pd.DataFrame]:
        """
        Fetch specific admin's data from all tables.
        
        Args:
            admin_id: Admin UUID
            limit: Number of recent records to fetch
            
        Returns:
            Dictionary containing DataFrames for each data type
        """
        result = {
            'calls': pd.DataFrame(),
            'ratings': pd.DataFrame(),  
            'leaves': pd.DataFrame()
        }
        
        try:
            # Get call data
            variables = {'limit': limit, 'admin_id': admin_id}
            call_data = self.client.execute_query(CALL_DATA_QUERY, variables)
            if call_data.get('whatsub_delivery_time'):
                result['calls'] = pd.DataFrame(call_data['whatsub_delivery_time'])
                result['calls']['created_at'] = pd.to_datetime(result['calls']['created_at'])
            
            # Get chat ratings (using user_id same as admin_id)
            variables = {'limit': limit, 'user_id': admin_id}
            rating_data = self.client.execute_query(CHAT_RATINGS_QUERY, variables)
            if rating_data.get('whatsub_admin_ratings'):
                result['ratings'] = pd.DataFrame(rating_data['whatsub_admin_ratings'])
                result['ratings']['created_at'] = pd.to_datetime(result['ratings']['created_at'])
            
            # Get leave requests
            variables = {'user_id': admin_id}
            leave_data = self.client.execute_query(LEAVE_REQUESTS_QUERY, variables)
            if leave_data.get('whatsub_room_user_mapping'):
                result['leaves'] = pd.DataFrame(leave_data['whatsub_room_user_mapping'])
                result['leaves']['created_at'] = pd.to_datetime(result['leaves']['created_at'])
            
        except Exception as e:
            print(f"Error fetching admin-specific data: {str(e)}")
        
        return result