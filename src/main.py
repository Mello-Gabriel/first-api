import os
from connector import BigQueryConnector
from flask import Flask, request


app = Flask(__name__)


@app.route("/")
def hello_world():
    """Example Hello World route."""
    name = os.environ.get("NAME", "World")
    return f"Hello {name}!"


@app.route("/query", methods=["POST"])
def query_bq():
    """
    Receives a JSON POST request with 'bigqueryprojectid' and 'sql_query',
    executes the query on BigQuery, and returns the result as JSON.
    """
    try:
        # The request body should be a JSON object containing the necessary parameters.
        request_data = request.get_json()
        if not request_data:
            return "Invalid JSON in request body", 400

        project_id = request_data.get("bigqueryprojectid")
        sql_query = request_data.get("sql_query")

        if not all([project_id, sql_query]):
            return "Missing 'bigqueryprojectid' or 'sql_query' in request", 400

        # Path to your credentials file
        credentials_file = ".keys/gen-lang-client-0298993137-2c8e72abd340.json"

        # Pass the credentials path to the connector
        connection = BigQueryConnector(project_id, credentials_path=credentials_file)

        # Query BigQuery and get a DataFrame
        df = connection.query_to_df(sql_query)

        # FIX: Convert the DataFrame to a JSON string to be returned in the response.
        # 'orient="records"' creates a list of record objects, e.g., [{"col1": "val1"}, {"col1": "val2"}].
        json_result = df.to_json(orient="records")

        # Return the JSON result with the correct content type
        return app.response_class(
            response=json_result, status=200, mimetype="application/json"
        )

    except FileNotFoundError:
        return f"Credentials file not found at path: {credentials_file}", 500
    except Exception as e:
        # Return a more descriptive error message
        return f"An error occurred: {e}", 400


if __name__ == "__main__":
    # Changed port to 5000 to match your curl command
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
