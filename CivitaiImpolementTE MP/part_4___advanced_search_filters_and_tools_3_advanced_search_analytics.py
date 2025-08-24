# Part 4 - Advanced Search Filters and Tools - 3. Advanced Search Analytics
# Generated for comprehensive CivitAI browser implementation


# Search analytics and insights

import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import pandas as pd

class SearchAnalytics:
    def __init__(self):
        if "search_history" not in st.session_state:
            st.session_state.search_history = []

    def log_search(self, params, results_count, execution_time):
        """Log search for analytics"""

        search_log = {
            "timestamp": datetime.now().isoformat(),
            "params": params,
            "results_count": results_count,
            "execution_time": execution_time,
            "search_type": "model" if "types" in params else "general"
        }

        st.session_state.search_history.append(search_log)

        # Keep only last 100 searches
        if len(st.session_state.search_history) > 100:
            st.session_state.search_history = st.session_state.search_history[-100:]

    def create_analytics_dashboard(self):
        """Create analytics dashboard"""

        if not st.session_state.search_history:
            st.info("No search history available yet.")
            return

        st.subheader("📊 Search Analytics")

        history = st.session_state.search_history

        # Convert to DataFrame
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date

        # Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Searches", len(history))

        with col2:
            avg_results = sum(h['results_count'] for h in history) / len(history)
            st.metric("Avg Results", f"{avg_results:.1f}")

        with col3:
            avg_time = sum(h['execution_time'] for h in history) / len(history)
            st.metric("Avg Time", f"{avg_time:.2f}s")

        with col4:
            success_rate = len([h for h in history if h['results_count'] > 0]) / len(history) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            # Searches over time
            daily_searches = df.groupby('date').size()

            fig = px.line(
                x=daily_searches.index, 
                y=daily_searches.values,
                title="Searches Over Time",
                labels={'x': 'Date', 'y': 'Number of Searches'}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Search types distribution
            search_types = Counter(h['search_type'] for h in history)

            fig = px.pie(
                values=list(search_types.values()),
                names=list(search_types.keys()),
                title="Search Types Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Popular search terms
        st.subheader("📈 Popular Search Terms")

        all_queries = [h['params'].get('query', '') for h in history if h['params'].get('query')]
        query_words = []

        for query in all_queries:
            query_words.extend(query.lower().split())

        if query_words:
            word_counts = Counter(query_words)
            popular_words = word_counts.most_common(10)

            fig = px.bar(
                x=[word for word, count in popular_words],
                y=[count for word, count in popular_words],
                title="Most Searched Terms",
                labels={'x': 'Search Terms', 'y': 'Frequency'}
            )
            st.plotly_chart(fig, use_container_width=True)

        # Filter usage
        st.subheader("🔧 Filter Usage")

        filter_usage = Counter()

        for search in history:
            params = search['params']
            if params.get('types'):
                for model_type in params['types']:
                    filter_usage[f"Type: {model_type}"] += 1
            if params.get('baseModels'):
                for base_model in params['baseModels']:
                    filter_usage[f"Base: {base_model}"] += 1
            if params.get('sort'):
                filter_usage[f"Sort: {params['sort']}"] += 1

        if filter_usage:
            most_used_filters = filter_usage.most_common(10)

            fig = px.bar(
                x=[count for filter_name, count in most_used_filters],
                y=[filter_name for filter_name, count in most_used_filters],
                orientation='h',
                title="Most Used Filters",
                labels={'x': 'Usage Count', 'y': 'Filter'}
            )
            st.plotly_chart(fig, use_container_width=True)

        # Export search history
        if st.button("📥 Export Search History"):
            csv_data = pd.DataFrame(history).to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv_data,
                "civitai_search_history.csv",
                "text/csv"
            )

# Performance monitoring
class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.metrics = {}

    def start_timing(self):
        self.start_time = time.time()

    def end_timing(self, operation_name):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics[operation_name] = duration
            return duration
        return 0

    def create_performance_display(self):
        """Display performance metrics"""

        if not self.metrics:
            return

        st.subheader("⚡ Performance Metrics")

        for operation, duration in self.metrics.items():
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.write(f"**{operation}**")

            with col2:
                st.write(f"{duration:.2f}s")

            with col3:
                # Performance indicator
                if duration < 1.0:
                    st.success("Fast")
                elif duration < 3.0:
                    st.warning("Moderate")
                else:
                    st.error("Slow")

# Integrated advanced search with analytics
def create_analytics_enhanced_search():
    st.title("📊 CivitAI Browser with Analytics")

    # Initialize components
    search_engine = AdvancedCivitAISearch()
    analytics = SearchAnalytics()
    performance = PerformanceMonitor()

    # Analytics dashboard in expander
    with st.expander("📊 View Analytics Dashboard"):
        analytics.create_analytics_dashboard()

    # Main search interface
    search_params = search_engine.create_search_interface()

    # Override search execution to include analytics
    if st.button("🔍 Search with Analytics", type="primary"):
        performance.start_timing()

        # Execute search (simplified for demo)
        with st.spinner("Searching..."):
            time.sleep(1)  # Simulate API call
            results_count = 42  # Mock results

        execution_time = performance.end_timing("Model Search")

        # Log search
        analytics.log_search(search_params, results_count, execution_time)

        # Display results
        st.success(f"Found {results_count} results in {execution_time:.2f}s")

        # Show performance metrics
        performance.create_performance_display()

if __name__ == "__main__":
    create_analytics_enhanced_search()
