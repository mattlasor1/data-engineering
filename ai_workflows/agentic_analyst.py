import json
import duckdb
from typing import Dict, Any

class AgenticDataAnalyst:
    """
    A simulated Agentic Workflow demonstrating tool/function calling
    and task decomposition, common in modern AI data engineering tasks.
    """
    
    def __init__(self, db_path: str = '../ecommerce.duckdb'):
        self.db_path = db_path
        
    def _execute_query(self, query: str) -> Any:
        try:
            con = duckdb.connect(self.db_path)
            result = con.execute(query).df()
            con.close()
            return result
        except Exception as e:
            return f"Error executing query: {str(e)}"

    def get_database_schema(self) -> str:
        """
        Tool 1: Retrieves the schema of the database to provide context to an LLM.
        """
        query = """
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'main'
        """
        df = self._execute_query(query)
        if isinstance(df, str):
            return df # Error
            
        schema_dict = {}
        for _, row in df.iterrows():
            table = row['table_name']
            col = row['column_name']
            dtype = row['data_type']
            if table not in schema_dict:
                schema_dict[table] = []
            schema_dict[table].append(f"{col} ({dtype})")
            
        return json.dumps(schema_dict, indent=2)

    def generate_sql_from_prompt(self, user_prompt: str) -> str:
        """
        Mock Tool 2: Simulates an LLM taking a prompt + schema and returning valid SQL.
        In a real scenario, this would be an OpenAI API call with JSON mode or function calling.
        """
        prompt_lower = user_prompt.lower()
        
        # Simple mock intent router
        if "revenue" in prompt_lower and "product" in prompt_lower:
            return """
            SELECT 
                p.product_name, 
                SUM(f.order_revenue) as total_revenue
            FROM fct_orders f
            JOIN dim_products p ON f.order_id IS NOT NULL -- Simplified join for mock
            GROUP BY p.product_name
            ORDER BY total_revenue DESC
            LIMIT 5;
            """
        elif "conversion" in prompt_lower or "rate" in prompt_lower:
            return """
            SELECT 
                status, 
                COUNT(*) as count,
                COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
            FROM fct_orders
            GROUP BY status;
            """
        else:
            return "SELECT * FROM fct_orders LIMIT 5;"

    def run_agentic_workflow(self, user_prompt: str) -> Dict[str, Any]:
        """
        Orchestrates the multi-step agentic workflow:
        1. Get Schema Context
        2. Generate SQL
        3. Execute SQL
        4. Return Structured Output
        """
        schema = self.get_database_schema()
        sql_query = self.generate_sql_from_prompt(user_prompt)
        
        # In a real workflow, the LLM might decide to run this tool multiple times
        # to fix syntax errors (Human-in-the-loop / Self-correction)
        result_df = self._execute_query(sql_query)
        
        return {
            "step_1_schema_retrieved": True,
            "step_2_generated_sql": sql_query.strip(),
            "step_3_execution_success": not isinstance(result_df, str),
            "final_result": result_df.to_dict('records') if not isinstance(result_df, str) else result_df
        }

if __name__ == "__main__":
    # Test the mock workflow
    agent = AgenticDataAnalyst('ecommerce.duckdb') # Local path for testing
    print("Testing Schema Tool:")
    print(agent.get_database_schema())
    
    print("\nTesting End-to-End Workflow:")
    result = agent.run_agentic_workflow("What are the top 5 products by revenue?")
    print(json.dumps(result, indent=2, default=str))
