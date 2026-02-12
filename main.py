"""
Main script for admin lambda ranking system.
"""
import sys
import pandas as pd
from typing import Optional
from admin_ranking import AdminRanking
from output_handler import OutputHandler


def main():
    """Main function to execute admin ranking process."""
    print("🚀 Starting Admin Lambda Ranking System")
    print("=" * 50)
    
    try:
        # Initialize components
        ranking_calculator = AdminRanking()
        output_handler = OutputHandler()
        
        # Calculate rankings for all admins
        print("\n📊 Calculating admin rankings...")
        rankings_df = ranking_calculator.rank_all_admins()
        
        if rankings_df.empty:
            print("❌ No ranking data available. Please check your database connection and data.")
            return
        
        # Display results
        print("\n🏆 Top 10 Admin Rankings:")
        output_handler.display_rankings(rankings_df, top_n=10)
        
        # Generate insights
        print("\n🔍 Generating performance insights...")
        insights = output_handler.generate_ranking_insights(rankings_df)
        
        print(f"\nPERFORMANCE DISTRIBUTION:")
        dist = insights['performance_distribution']
        print(f"  🌟 Excellent: {dist['excellent']} admins")
        print(f"  👍 Good: {dist['good']} admins")
        print(f"  📊 Average: {dist['average']} admins")
        print(f"  📉 Below Average: {dist['below_average']} admins")
        
        print(f"\nTOP PERFORMERS BY CATEGORY:")
        comp = insights['component_analysis']
        print(f"  🎯 Best Call Rating: {comp['strongest_in_call_rating']}")
        print(f"  ⚡ Fastest Delivery: {comp['fastest_delivery']}")
        print(f"  💬 Best Chat Rating: {comp['best_chat_rating']}")
        print(f"  ✅ Highest Availability: {comp['highest_availability']}")
        
        # Save outputs
        print("\n💾 Saving results...")
        csv_path = output_handler.save_to_csv(rankings_df)
        report_path = output_handler.save_detailed_report(rankings_df, insights)
        
        # Export top performers
        top_performers = output_handler.export_top_performers(rankings_df, percentile=20)
        
        print(f"\n✅ Process completed successfully!")
        print(f"   📁 CSV Rankings: {csv_path}")
        print(f"   📄 Detailed Report: {report_path}")
        print(f"   ⭐ Top 20% exported: {len(top_performers)} admins")
        
    except Exception as e:
        print(f"❌ Error during execution: {str(e)}")
        sys.exit(1)


def analyze_specific_admin(admin_id: str):
    """
    Analyze a specific admin in detail.
    
    Args:
        admin_id: Admin UUID to analyze
    """
    print(f"🔍 Analyzing Admin: {admin_id}")
    print("=" * 50)
    
    try:
        ranking_calculator = AdminRanking()
        output_handler = OutputHandler()
        
        # Get detailed analysis
        analysis = ranking_calculator.get_admin_detailed_analysis(admin_id)
        
        # Display analysis
        output_handler.display_admin_analysis(analysis)
        
        # Save detailed analysis
        report_path = output_handler.save_detailed_report(pd.DataFrame(), analysis)
        print(f"\n💾 Detailed analysis saved to: {report_path}")
        
    except Exception as e:
        print(f"❌ Error analyzing admin: {str(e)}")


def get_top_admins(n: int = 5):
    """
    Get and display top N admins.
    
    Args:
        n: Number of top admins to display
    """
    print(f"🏆 Getting Top {n} Admins")
    print("=" * 30)
    
    try:
        ranking_calculator = AdminRanking()
        output_handler = OutputHandler()
        
        top_admins = ranking_calculator.get_top_admins(top_n=n)
        output_handler.display_rankings(top_admins, top_n=n)
        
    except Exception as e:
        print(f"❌ Error getting top admins: {str(e)}")


if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'analyze' and len(sys.argv) > 2:
            admin_id = sys.argv[2]
            analyze_specific_admin(admin_id)
        elif command == 'top' and len(sys.argv) > 2:
            try:
                n = int(sys.argv[2])
                get_top_admins(n)
            except ValueError:
                print("❌ Please provide a valid number for top N admins")
        else:
            print("Usage:")
            print("  python main.py                    # Run full ranking")
            print("  python main.py analyze <admin_id> # Analyze specific admin")
            print("  python main.py top <n>           # Get top N admins")
    else:
        # Run full ranking process
        main()