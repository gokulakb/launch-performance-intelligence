"""
Reusable SQL queries for the Launch Performance Intelligence Dashboard.
All queries are parameterized and optimized for performance.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from database.database import db

class Queries:
    """Collection of reusable SQL queries."""
    
    def __init__(self):
        self.db = db
    
    # ===== User Queries =====
    
    def get_user_count(self, company: str = None, date_from: str = None, date_to: str = None) -> int:
        """Get total user count with optional filters."""
        query = "SELECT COUNT(*) as count FROM users WHERE 1=1"
        params = {}
        
        if company:
            query += " AND company = :company"
            params['company'] = company
        if date_from:
            query += " AND signup_date >= :date_from"
            params['date_from'] = date_from
        if date_to:
            query += " AND signup_date <= :date_to"
            params['date_to'] = date_to
        
        result = self.db.execute_query(query, params)
        return int(result['count'].iloc[0]) if not result.empty else 0
    
    def get_active_users(self, company: str = None, days: int = 30) -> int:
        """Get count of active users within the last N days."""
        query = """
            SELECT COUNT(DISTINCT user_id) as count 
            FROM events 
            WHERE timestamp >= datetime('now', :interval)
        """
        params = {'interval': f'-{days} days'}
        
        if company:
            query += " AND user_id IN (SELECT user_id FROM users WHERE company = :company)"
            params['company'] = company
        
        result = self.db.execute_query(query, params)
        return int(result['count'].iloc[0]) if not result.empty else 0
    
    def get_user_metrics(self, company: str = None) -> pd.DataFrame:
        """Get comprehensive user metrics."""
        query = """
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_users,
                SUM(CASE WHEN profile_completed = 1 THEN 1 ELSE 0 END) as profile_completed,
                AVG(CASE WHEN profile_completed = 1 THEN 1 ELSE 0 END) as completion_rate,
                COUNT(DISTINCT college) as colleges,
                COUNT(DISTINCT company) as companies
            FROM users
        """
        params = {}
        if company:
            query += " WHERE company = :company"
            params['company'] = company
        
        return self.db.execute_query(query, params)
    
    # ===== Event Queries =====
    
    def get_event_funnel(self, company: str = None, date_from: str = None, date_to: str = None) -> Dict[str, int]:
        """Get funnel data for events."""
        funnel_events = [
            'visitor', 'signup', 'profile_complete', 
            'application', 'interview', 'offer', 'hire'
        ]
        
        query = """
            SELECT 
                event_type,
                COUNT(DISTINCT user_id) as user_count
            FROM events
            WHERE event_type IN :event_types
        """
        params = {'event_types': tuple(funnel_events)}
        
        if company:
            query += " AND user_id IN (SELECT user_id FROM users WHERE company = :company)"
            params['company'] = company
        if date_from:
            query += " AND timestamp >= :date_from"
            params['date_from'] = date_from
        if date_to:
            query += " AND timestamp <= :date_to"
            params['date_to'] = date_to
        
        query += " GROUP BY event_type ORDER BY CASE event_type"
        for i, event in enumerate(funnel_events):
            query += f" WHEN '{event}' THEN {i}"
        query += " END"
        
        result = self.db.execute_query(query, params)
        return dict(zip(result['event_type'], result['user_count'])) if not result.empty else {}
    
    def get_session_metrics(self, company: str = None, days: int = 30) -> pd.DataFrame:
        """Get session metrics for users."""
        query = """
            SELECT 
                user_id,
                COUNT(DISTINCT session_id) as sessions,
                AVG(duration) as avg_duration,
                COUNT(*) as events
            FROM events
            WHERE timestamp >= datetime('now', :interval)
        """
        params = {'interval': f'-{days} days'}
        
        if company:
            query += " AND user_id IN (SELECT user_id FROM users WHERE company = :company)"
            params['company'] = company
        
        query += " GROUP BY user_id"
        
        return self.db.execute_query(query, params)
    
    # ===== Revenue Queries =====
    
    def get_revenue_by_date(self, company: str = None, date_from: str = None, date_to: str = None) -> pd.DataFrame:
        """Get revenue aggregated by date."""
        query = """
            SELECT 
                transaction_date as date,
                SUM(amount) as revenue,
                COUNT(*) as transactions,
                AVG(amount) as avg_transaction
            FROM revenue
            WHERE 1=1
        """
        params = {}
        
        if company:
            query += " AND company = :company"
            params['company'] = company
        if date_from:
            query += " AND transaction_date >= :date_from"
            params['date_from'] = date_from
        if date_to:
            query += " AND transaction_date <= :date_to"
            params['date_to'] = date_to
        
        query += " GROUP BY transaction_date ORDER BY transaction_date"
        
        return self.db.execute_query(query, params)
    
    def get_revenue_by_company(self, date_from: str = None, date_to: str = None) -> pd.DataFrame:
        """Get revenue aggregated by company."""
        query = """
            SELECT 
                company,
                SUM(amount) as revenue,
                COUNT(*) as transactions,
                AVG(amount) as avg_transaction
            FROM revenue
            WHERE 1=1
        """
        params = {}
        
        if date_from:
            query += " AND transaction_date >= :date_from"
            params['date_from'] = date_from
        if date_to:
            query += " AND transaction_date <= :date_to"
            params['date_to'] = date_to
        
        query += " GROUP BY company ORDER BY revenue DESC"
        
        return self.db.execute_query(query, params)
    
    def get_revenue_by_recruiter(self, company: str = None) -> pd.DataFrame:
        """Get revenue aggregated by recruiter."""
        query = """
            SELECT 
                recruiter,
                company,
                SUM(amount) as revenue,
                COUNT(*) as transactions
            FROM revenue
            WHERE 1=1
        """
        params = {}
        
        if company:
            query += " AND company = :company"
            params['company'] = company
        
        query += " GROUP BY recruiter, company ORDER BY revenue DESC"
        
        return self.db.execute_query(query, params)
    
    def get_mrr(self, company: str = None) -> float:
        """Calculate Monthly Recurring Revenue."""
        query = """
            SELECT SUM(amount) / 12 as mrr
            FROM revenue
            WHERE transaction_date >= date('now', '-1 year')
        """
        params = {}
        
        if company:
            query += " AND company = :company"
            params['company'] = company
        
        result = self.db.execute_query(query, params)
        return float(result['mrr'].iloc[0]) if not result.empty else 0.0
    
    # ===== Retention Queries =====
    
    def get_retention_rates(self, company: str = None, cohort: str = None) -> pd.DataFrame:
        """Get retention rates by cohort."""
        query = """
            SELECT 
                cohort,
                COUNT(*) as total_users,
                SUM(CASE WHEN day_1_retained = 1 THEN 1 ELSE 0 END) as day_1_retained,
                SUM(CASE WHEN day_7_retained = 1 THEN 1 ELSE 0 END) as day_7_retained,
                SUM(CASE WHEN day_30_retained = 1 THEN 1 ELSE 0 END) as day_30_retained,
                SUM(CASE WHEN week_4_retained = 1 THEN 1 ELSE 0 END) as week_4_retained,
                SUM(CASE WHEN monthly_retained = 1 THEN 1 ELSE 0 END) as monthly_retained,
                AVG(CASE WHEN day_1_retained = 1 THEN 1 ELSE 0 END) * 100 as retention_rate_d1,
                AVG(CASE WHEN day_7_retained = 1 THEN 1 ELSE 0 END) * 100 as retention_rate_d7,
                AVG(CASE WHEN day_30_retained = 1 THEN 1 ELSE 0 END) * 100 as retention_rate_d30,
                AVG(CASE WHEN week_4_retained = 1 THEN 1 ELSE 0 END) * 100 as retention_rate_w4,
                AVG(CASE WHEN monthly_retained = 1 THEN 1 ELSE 0 END) * 100 as retention_rate_monthly
            FROM retention
            WHERE 1=1
        """
        params = {}
        
        if company:
            query += " AND company = :company"
            params['company'] = company
        if cohort:
            query += " AND cohort = :cohort"
            params['cohort'] = cohort
        
        query += " GROUP BY cohort ORDER BY cohort"
        
        return self.db.execute_query(query, params)
    
    def get_cohort_analysis(self, company: str = None) -> pd.DataFrame:
        """Get cohort analysis data for heatmap."""
        query = """
            WITH cohort_data AS (
                SELECT 
                    cohort,
                    DATE(signup_date, 'start of month') as signup_month,
                    (strftime('%Y', CURRENT_DATE) * 12 + strftime('%m', CURRENT_DATE)) - 
                    (strftime('%Y', signup_date) * 12 + strftime('%m', signup_date)) as months_since_signup,
                    COUNT(*) as users
                FROM retention
                WHERE 1=1
        """
        params = {}
        
        if company:
            query += " AND company = :company"
            params['company'] = company
        
        query += """
                GROUP BY cohort, signup_month
            )
            SELECT 
                cohort,
                months_since_signup,
                users,
                users * 1.0 / FIRST_VALUE(users) OVER (PARTITION BY cohort ORDER BY months_since_signup) * 100 as retention_pct
            FROM cohort_data
            ORDER BY cohort, months_since_signup
        """
        
        return self.db.execute_query(query, params)
    
    def get_churn_metrics(self, company: str = None) -> pd.DataFrame:
        """Get churn metrics."""
        query = """
            SELECT 
                cohort,
                COUNT(*) as total_users,
                SUM(CASE WHEN churned = 1 THEN 1 ELSE 0 END) as churned_users,
                AVG(CASE WHEN churned = 1 THEN 1 ELSE 0 END) * 100 as churn_rate
            FROM retention
            WHERE 1=1
        """
        params = {}
        
        if company:
            query += " AND company = :company"
            params['company'] = company
        
        query += " GROUP BY cohort ORDER BY cohort"
        
        return self.db.execute_query(query, params)
    
    # ===== Quality Queries =====
    
    def get_quality_metrics(self, table_name: str = None) -> pd.DataFrame:
        """Get data quality metrics."""
        query = "SELECT * FROM quality_metrics WHERE 1=1"
        params = {}
        
        if table_name:
            query += " AND table_name = :table_name"
            params['table_name'] = table_name
        
        query += " ORDER BY last_refresh DESC"
        
        return self.db.execute_query(query, params)
    
    def get_table_completeness(self, table_name: str) -> Dict[str, Any]:
        """Calculate completeness for a table."""
        # Get table info
        table_info = self.db.get_table_info(table_name)
        columns = [col['name'] for col in table_info['columns']]
        
        query = "SELECT COUNT(*) as total FROM {table_name}"
        total_result = self.db.execute_query(query.format(table_name=table_name))
        total = int(total_result['total'].iloc[0]) if not total_result.empty else 0
        
        if total == 0:
            return None
        
        completeness_data = {}
        for column in columns:
            query = f"""
                SELECT 
                    COUNT(*) as count,
                    SUM(CASE WHEN {column} IS NULL THEN 1 ELSE 0 END) as null_count,
                    SUM(CASE WHEN {column} = '' THEN 1 ELSE 0 END) as empty_count
                FROM {table_name}
            """
            result = self.db.execute_query(query)
            
            if not result.empty:
                null_count = int(result['null_count'].iloc[0])
                empty_count = int(result['empty_count'].iloc[0])
                valid_count = total - null_count - empty_count
                completeness = valid_count / total if total > 0 else 0
                
                completeness_data[column] = {
                    'total': total,
                    'null_count': null_count,
                    'empty_count': empty_count,
                    'valid_count': valid_count,
                    'completeness': completeness
                }
        
        return {
            'metric_name': f'{table_name}_completeness',
            'metric_type': 'completeness',
            'table_name': table_name,
            'value': sum(d['completeness'] for d in completeness_data.values()) / len(completeness_data),
            'sample_size': total,
            'total_count': total,
            'null_count': sum(d['null_count'] for d in completeness_data.values()),
            'duplicate_count': 0,
            'anomaly_count': 0,
            'validation_status': 'valid' if completeness >= 0.95 else 'warning',
            'confidence': 0.95,
            'last_refresh': datetime.now()
        }
    
    # ===== Launch Metrics Queries =====
    
    def get_launch_metrics(self, company: str = None, date_from: str = None, date_to: str = None) -> pd.DataFrame:
        """Get launch performance metrics."""
        query = "SELECT * FROM launch_metrics WHERE 1=1"
        params = {}
        
        if company:
            query += " AND company = :company"
            params['company'] = company
        if date_from:
            query += " AND metric_date >= :date_from"
            params['date_from'] = date_from
        if date_to:
            query += " AND metric_date <= :date_to"
            params['date_to'] = date_to
        
        query += " ORDER BY metric_date"
        
        return self.db.execute_query(query, params)
    
    def get_latest_metrics(self, company: str = None) -> Dict[str, Any]:
        """Get the latest metrics for a company."""
        query = """
            SELECT 
                visitors,
                active_users,
                signups,
                applications,
                interviews,
                offers,
                hires,
                revenue,
                retention_rate,
                quality_score
            FROM launch_metrics
        """
        params = {}
        
        if company:
            query += " WHERE company = :company"
            params['company'] = company
        
        query += " ORDER BY metric_date DESC LIMIT 1"
        
        result = self.db.execute_query(query, params)
        return result.iloc[0].to_dict() if not result.empty else {}
    
    # ===== Combined Queries =====
    
    def get_dashboard_summary(self, company: str = None) -> Dict[str, Any]:
        """Get comprehensive dashboard summary."""
        summary = {
            'users': self.get_user_count(company),
            'active_users': self.get_active_users(company),
            'revenue_total': 0,
            'retention_d1': 0,
            'retention_d7': 0,
            'retention_d30': 0,
            'quality_score': 0,
            'latest_metrics': self.get_latest_metrics(company)
        }
        
        # Get revenue
        revenue_df = self.get_revenue_by_date(company)
        if not revenue_df.empty:
            summary['revenue_total'] = revenue_df['revenue'].sum()
        
        # Get retention
        retention_df = self.get_retention_rates(company)
        if not retention_df.empty:
            latest_cohort = retention_df.iloc[-1]
            summary['retention_d1'] = latest_cohort.get('retention_rate_d1', 0)
            summary['retention_d7'] = latest_cohort.get('retention_rate_d7', 0)
            summary['retention_d30'] = latest_cohort.get('retention_rate_d30', 0)
        
        # Get quality
        quality_df = self.get_quality_metrics()
        if not quality_df.empty:
            summary['quality_score'] = quality_df['value'].mean()
        
        return summary
    
    def get_problem_ranking_data(self, company: str = None) -> pd.DataFrame:
        """Get data for problem ranking analysis."""
        # This query aggregates various metrics to identify problems
        query = """
            WITH metrics AS (
                SELECT 
                    'user_engagement' as category,
                    COUNT(*) as total,
                    SUM(CASE WHEN last_active < date('now', '-30 days') THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as issue_rate
                FROM users
            )
            SELECT 
                category,
                issue_rate,
                'user' as metric_type
            FROM metrics
            UNION ALL
            SELECT 
                'revenue_drop' as category,
                (1 - (SELECT SUM(amount) FROM revenue WHERE transaction_date >= date('now', '-30 days')) / 
                (SELECT SUM(amount) FROM revenue WHERE transaction_date >= date('now', '-60 days') AND transaction_date < date('now', '-30 days'))) * 100 as issue_rate,
                'revenue' as metric_type
            UNION ALL
            SELECT 
                'retention_decline' as category,
                100 - AVG(retention_rate_d7) as issue_rate,
                'retention' as metric_type
            FROM retention
        """
        params = {}
        if company:
            query += " WHERE company = :company"
            params['company'] = company
        
        return self.db.execute_query(query, params)