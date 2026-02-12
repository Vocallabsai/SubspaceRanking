"""
Experimental admin ranking with normalized and weighted formula.
"""
import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_fetcher import AdminDataFetcher

# Weights for each metric (adjust as needed)
WEIGHTS = {
    'cr50': 2.0,   # Call rating (normalized)
    'r50': 2.0,    # Chat rating (normalized)
    'cdt50': 1.0,  # Delivery time (normalized, higher is better)
    'lr1m': 1.0    # Leave requests (normalized, higher is better)
}

# Reasonable max delivery time (seconds) for normalization
MAX_DELIVERY_TIME = 60.0


def normalize_rating(val, max_val=5.0):
    return min(val / max_val, 1.0) if val is not None else 0.0

def normalize_delivery_time(avg_time):
    if avg_time is None or avg_time <= 0:
        return 1.0
    norm = min(MAX_DELIVERY_TIME / avg_time, 1.0)
    return norm

def normalize_leaves(leave_count):
    return min(1.0, 1.0 / (leave_count + 1))


def calculate_experiment_lambda(cr50, r50, cdt50, lr1m):
    cr50_norm = normalize_rating(cr50)
    r50_norm = normalize_rating(r50)
    cdt50_norm = normalize_delivery_time(cdt50)
    lr1m_norm = normalize_leaves(lr1m)
    score = (
        WEIGHTS['cr50'] * cr50_norm +
        WEIGHTS['r50'] * r50_norm +
        WEIGHTS['cdt50'] * cdt50_norm +
        WEIGHTS['lr1m'] * lr1m_norm
    )
    return score, cr50_norm, r50_norm, cdt50_norm, lr1m_norm


def run_experiment():
    fetcher = AdminDataFetcher()
    call_data = fetcher.get_all_call_data()
    rating_data = fetcher.get_all_chat_ratings()
    leave_data = fetcher.get_all_leave_requests()
    if call_data.empty:
        print("No call data available.")
        return
    admin_ids = call_data['admin_id'].unique()
    results = []
    for admin_id in admin_ids:
        admin_calls = call_data[call_data['admin_id'] == admin_id].sort_values('created_at', ascending=False).head(50)
        cr50 = admin_calls['internal_rating'].dropna().mean() if not admin_calls.empty else 0.0
        cdt50 = admin_calls['credentials_delivery_time'].dropna().mean() if not admin_calls.empty else MAX_DELIVERY_TIME
        admin_ratings = rating_data[rating_data['user_id'] == admin_id].sort_values('created_at', ascending=False).head(50)
        r50 = admin_ratings['rating'].dropna().mean() if not admin_ratings.empty else 0.0
        if leave_data.empty or 'user_id' not in leave_data.columns:
            lr1m = 0
        else:
            admin_leaves = leave_data[leave_data['user_id'] == admin_id]
            lr1m = len(admin_leaves)
        score, cr50_norm, r50_norm, cdt50_norm, lr1m_norm = calculate_experiment_lambda(cr50, r50, cdt50, lr1m)
        admin_name = admin_calls['admin_name'].iloc[0] if not admin_calls.empty else 'Unknown'
        results.append({
            'admin_id': admin_id,
            'admin_name': admin_name,
            'exp_lambda_score': score,
            'cr50': cr50,
            'cr50_norm': cr50_norm,
            'r50': r50,
            'r50_norm': r50_norm,
            'cdt50': cdt50,
            'cdt50_norm': cdt50_norm,
            'lr1m': lr1m,
            'lr1m_norm': lr1m_norm
        })
    df = pd.DataFrame(results)
    df = df.sort_values('exp_lambda_score', ascending=False).reset_index(drop=True)
    df['rank'] = df.index + 1
    out_base = os.path.join(os.path.dirname(__file__), 'experiment_admin_rankings')
    out_xlsx = out_base + '.xlsx'
    out_csv = out_base + '.csv'
    df.to_excel(out_xlsx, index=False)
    df.to_csv(out_csv, index=False)
    print(f"\nExperimental rankings saved to: {out_xlsx} and {out_csv}\n")
    print(df[['rank','admin_name','exp_lambda_score','cr50','r50','cdt50','lr1m']].head(10))

if __name__ == "__main__":
    run_experiment()
