"""
Configuration settings for the admin ranking system.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Hasura Configuration
HASURA_ENDPOINT = os.getenv('HASURA_ENDPOINT')
HASURA_ADMIN_SECRET = os.getenv('HASURA_ADMIN_SECRET')

# GraphQL Queries
CALL_DATA_QUERY = """
query GetCallData($limit: Int!, $admin_id: uuid) {
  whatsub_delivery_time(
    where: {admin_id: {_eq: $admin_id}}
    order_by: {created_at: desc}
    limit: $limit
  ) {
    id
    admin_id
    admin_name
    internal_rating
    credentials_delivery_time
    created_at
    call_status
  }
}
"""

ALL_ADMINS_CALL_DATA_QUERY = """
query GetAllAdminsCallData($limit: Int!) {
  whatsub_delivery_time(
    where: {admin_id: {_is_null: false}}
    order_by: {created_at: desc}
    limit: $limit
  ) {
    id
    admin_id
    admin_name
    internal_rating
    credentials_delivery_time
    created_at
    call_status
  }
}
"""

CHAT_RATINGS_QUERY = """
query GetChatRatings($limit: Int!, $user_id: uuid) {
  whatsub_admin_ratings(
    where: {user_id: {_eq: $user_id}}
    order_by: {created_at: desc}
    limit: $limit
  ) {
    id
    user_id
    rating
    created_at
    operation_status
  }
}
"""

ALL_CHAT_RATINGS_QUERY = """
query GetAllChatRatings($limit: Int!) {
  whatsub_admin_ratings(
    where: {user_id: {_is_null: false}}
    order_by: {created_at: desc}
    limit: $limit
  ) {
    id
    user_id
    rating
    created_at
    operation_status
  }
}
"""

LEAVE_REQUESTS_QUERY = """
query GetLeaveRequests($user_id: uuid) {
  whatsub_room_user_mapping(
    where: {
      user_id: {_eq: $user_id}
      leave_request: {_eq: true}
      created_at: {_gte: "2026-01-12T00:00:00Z"}
    }
    order_by: {created_at: desc}
  ) {
    id
    user_id
    leave_request
    leave_request_reason
    created_at
  }
}
"""

ALL_LEAVE_REQUESTS_QUERY = """
query GetAllLeaveRequests {
  whatsub_room_user_mapping(
    where: {
      leave_request: {_eq: true}
      created_at: {_gte: "2026-01-12T00:00:00Z"}
    }
    order_by: {created_at: desc}
  ) {
    id
    user_id
    leave_request
    leave_request_reason
    created_at
  }
}
"""

# Configuration Parameters
RECENT_CALLS_LIMIT = 50
RECENT_RATINGS_LIMIT = 50
DAYS_FOR_LEAVE_REQUESTS = 30