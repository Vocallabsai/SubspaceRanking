"""
Output handler for formatting and displaying admin ranking results.
"""
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Optional


class OutputHandler:
    """Handles formatting and output of ranking results."""
    
    def __init__(self):
        """Initialize the output handler."""
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def display_rankings(self, rankings_df: pd.DataFrame, top_n: int = 10) -> None:
        """
        Display rankings in console format.
        
        Args:
            rankings_df: DataFrame with admin rankings
            top_n: Number of top admins to display
        """
        if rankings_df.empty:
            print("No rankings data to display")
            return
        
        top_admins = rankings_df.head(top_n)
        
        print(f"\n{'='*80}")
        print(f"TOP {top_n} ADMIN RANKINGS BY LAMBDA SCORE")
        print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        print(f"{'Rank':<5} {'Admin Name':<20} {'Lambda Score':<12} {'CR50':<8} {'1/CDT50':<8} {'R50':<8} {'1/LR1M':<8}")
        print(f"{'-'*80}")
        
        for _, row in top_admins.iterrows():
            print(f"{row['rank']:<5} {str(row['admin_name'])[:19]:<20} "
                  f"{row['lambda_score']:<12.3f} {row['cr50']:<8.3f} "
                  f"{row['cdt50_inverse']:<8.3f} {row['r50']:<8.3f} {row['lr1m_inverse']:<8.3f}")
        
        print(f"\nTotal Admins Ranked: {len(rankings_df)}")
        
        # Display summary statistics
        print(f"\nSUMMARY STATISTICS:")
        print(f"Average Lambda Score: {rankings_df['lambda_score'].mean():.3f}")
        print(f"Highest Lambda Score: {rankings_df['lambda_score'].max():.3f}")
        print(f"Lowest Lambda Score: {rankings_df['lambda_score'].min():.3f}")
        print(f"Standard Deviation: {rankings_df['lambda_score'].std():.3f}")
    
    def save_to_csv(self, rankings_df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """
        Save rankings to CSV and Excel file.
        
        Args:
            rankings_df: DataFrame with admin rankings
            filename: Optional custom filename (without extension)
        Returns:
            Path to saved CSV file
        """
        import os
        if filename is None:
            filename = f"admin_rankings_{self.timestamp}"
        basepath = f"C:\\Users\\chait\\Desktop\\subspaceRanking\\{filename}"
        csv_path = basepath + ".csv"
        xlsx_path = basepath + ".xlsx"
        # Reorder columns for better readability
        column_order = [
            'rank', 'admin_id', 'admin_name', 'lambda_score',
            'cr50', 'cdt50_inverse', 'r50', 'lr1m_inverse'
        ]
        output_df = rankings_df[column_order].copy()
        output_df.to_csv(csv_path, index=False, float_format='%.3f')
        try:
            output_df.to_excel(xlsx_path, index=False, float_format='%.3f')
            print(f"\nRankings saved to: {csv_path} and {xlsx_path}")
        except Exception as e:
            print(f"\nRankings saved to: {csv_path}")
            print(f"(Excel export failed: {e})")
        return csv_path
    
    def save_detailed_report(self, rankings_df: pd.DataFrame, 
                           detailed_analysis: Optional[Dict] = None) -> str:
        """
        Save comprehensive report with rankings and analysis.
        
        Args:
            rankings_df: DataFrame with admin rankings
            detailed_analysis: Optional detailed analysis data
            
        Returns:
            Path to saved report file
        """
        filename = f"admin_ranking_report_{self.timestamp}.json"
        filepath = f"C:\\Users\\chait\\Desktop\\subspaceRanking\\{filename}"
        
        report_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_admins': len(rankings_df),
                'formula_used': 'lambda = cr50 + 1/cdt50 + r50 + 1/lr1m',
                'data_source': 'Hasura GraphQL - db.subspace.money'
            },
            'summary_statistics': {
                'avg_lambda_score': float(rankings_df['lambda_score'].mean()),
                'max_lambda_score': float(rankings_df['lambda_score'].max()),
                'min_lambda_score': float(rankings_df['lambda_score'].min()),
                'std_lambda_score': float(rankings_df['lambda_score'].std()),
                'avg_cr50': float(rankings_df['cr50'].mean()),
                'avg_cdt50_inverse': float(rankings_df['cdt50_inverse'].mean()),
                'avg_r50': float(rankings_df['r50'].mean()),
                'avg_lr1m_inverse': float(rankings_df['lr1m_inverse'].mean())
            },
            'rankings': rankings_df.to_dict('records'),
            'detailed_analysis': detailed_analysis
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Detailed report saved to: {filepath}")
        return filepath
    
    def display_admin_analysis(self, analysis_data: Dict) -> None:
        """
        Display detailed analysis for a specific admin and export all records to Excel.
        
        Args:
            analysis_data: Dictionary with admin analysis data
        """
        lambda_metrics = analysis_data['lambda_metrics']
        statistics = analysis_data['statistics']
        print(f"\n{'='*60}")
        print(f"DETAILED ADMIN ANALYSIS")
        print(f"Admin ID: {lambda_metrics['admin_id']}")
        print(f"{'='*60}")
        print(f"\nLAMBDA SCORE BREAKDOWN:")
        print(f"  Final Lambda Score: {lambda_metrics['lambda_score']:.3f}")
        print(f"  CR50 (Call Rating):     {lambda_metrics['cr50']:.3f}")
        print(f"  1/CDT50 (Delivery):     {lambda_metrics['cdt50_inverse']:.3f}")
        print(f"  R50 (Chat Rating):      {lambda_metrics['r50']:.3f}")
        print(f"  1/LR1M (Availability):  {lambda_metrics['lr1m_inverse']:.3f}")
        print(f"\nRECORD COUNTS:")
        print(f"  Total Calls: {statistics['total_calls']}")
        print(f"  Total Chat Ratings: {statistics['total_ratings']}")
        print(f"  Total Leave Requests: {statistics['total_leaves']}")
        print(f"\nAVERAGE METRICS:")
        print(f"  Average Call Rating: {statistics['avg_call_rating']:.3f}")
        print(f"  Average Delivery Time: {statistics['avg_delivery_time']:.1f} seconds")
        print(f"  Average Chat Rating: {statistics['avg_chat_rating']:.3f}")

        # Export all records to Excel for this admin
        import pandas as pd
        from datetime import datetime
        admin_id = lambda_metrics['admin_id']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"admin_{admin_id}_details_{timestamp}.xlsx"
        filepath = f"C:\\Users\\chait\\Desktop\\subspaceRanking\\{filename}"
        def remove_tz(df):
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].dt.tz_localize(None)
            return df
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            calls_df = pd.DataFrame(analysis_data['recent_calls'])
            ratings_df = pd.DataFrame(analysis_data['recent_ratings'])
            leaves_df = pd.DataFrame(analysis_data['recent_leaves'])
            calls_df = remove_tz(calls_df)
            ratings_df = remove_tz(ratings_df)
            leaves_df = remove_tz(leaves_df)
            calls_df.to_excel(writer, sheet_name='Calls', index=False)
            ratings_df.to_excel(writer, sheet_name='ChatRatings', index=False)
            leaves_df.to_excel(writer, sheet_name='Leaves', index=False)
        print(f"\nAll detailed records exported to: {filepath}")
    
    def export_top_performers(self, rankings_df: pd.DataFrame, 
                            percentile: int = 20) -> pd.DataFrame:
        """
        Export top performing admins based on percentile (CSV and Excel).
        
        Args:
            rankings_df: DataFrame with admin rankings
            percentile: Top percentile to export (e.g., 20 for top 20%)
        Returns:
            DataFrame with top performers
        """
        import os
        if rankings_df.empty:
            return pd.DataFrame()
        top_count = max(1, int(len(rankings_df) * (percentile / 100)))
        top_performers = rankings_df.head(top_count)
        filename = f"top_{percentile}_percent_admins_{self.timestamp}"
        basepath = f"C:\\Users\\chait\\Desktop\\subspaceRanking\\{filename}"
        csv_path = basepath + ".csv"
        xlsx_path = basepath + ".xlsx"
        top_performers.to_csv(csv_path, index=False, float_format='%.3f')
        try:
            top_performers.to_excel(xlsx_path, index=False, float_format='%.3f')
            print(f"\nTop {percentile}% performers ({top_count} admins) saved to: {csv_path} and {xlsx_path}")
        except Exception as e:
            print(f"\nTop {percentile}% performers ({top_count} admins) saved to: {csv_path}")
            print(f"(Excel export failed: {e})")
        return top_performers
    
    def generate_ranking_insights(self, rankings_df: pd.DataFrame) -> Dict[str, any]:
        """
        Generate insights from ranking data.
        
        Args:
            rankings_df: DataFrame with admin rankings
            
        Returns:
            Dictionary with insights and recommendations
        """
        if rankings_df.empty:
            return {}
        
        insights = {
            'performance_distribution': {
                'excellent': len(rankings_df[rankings_df['lambda_score'] >= rankings_df['lambda_score'].quantile(0.8)]),
                'good': len(rankings_df[(rankings_df['lambda_score'] >= rankings_df['lambda_score'].quantile(0.6)) & 
                                      (rankings_df['lambda_score'] < rankings_df['lambda_score'].quantile(0.8))]),
                'average': len(rankings_df[(rankings_df['lambda_score'] >= rankings_df['lambda_score'].quantile(0.4)) & 
                                         (rankings_df['lambda_score'] < rankings_df['lambda_score'].quantile(0.6))]),
                'below_average': len(rankings_df[rankings_df['lambda_score'] < rankings_df['lambda_score'].quantile(0.4)])
            },
            'component_analysis': {
                'strongest_in_call_rating': rankings_df.loc[rankings_df['cr50'].idxmax()]['admin_name'] if not rankings_df.empty else 'N/A',
                'fastest_delivery': rankings_df.loc[rankings_df['cdt50_inverse'].idxmax()]['admin_name'] if not rankings_df.empty else 'N/A',
                'best_chat_rating': rankings_df.loc[rankings_df['r50'].idxmax()]['admin_name'] if not rankings_df.empty else 'N/A',
                'highest_availability': rankings_df.loc[rankings_df['lr1m_inverse'].idxmax()]['admin_name'] if not rankings_df.empty else 'N/A'
            },
            'improvement_opportunities': {
                'low_call_ratings': rankings_df[rankings_df['cr50'] < rankings_df['cr50'].quantile(0.3)]['admin_name'].tolist(),
                'slow_delivery': rankings_df[rankings_df['cdt50_inverse'] < rankings_df['cdt50_inverse'].quantile(0.3)]['admin_name'].tolist(),
                'low_chat_ratings': rankings_df[rankings_df['r50'] < rankings_df['r50'].quantile(0.3)]['admin_name'].tolist()
            }
        }
        
        return insights