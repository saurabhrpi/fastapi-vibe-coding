from pymilvus import connections

HOST = "in03-874be76b9aa0be7.serverless.gcp-us-west1.cloud.zilliz.com"  # No https://
TOKEN = "268c3796886a41827afcee6560f083fbfc4992ae7265598b4d3582979748054380929293cd76ea79244845abf9773e4e9128de0e"  # Replace with your actual token

try:
    connections.connect(
        alias="default",
        uri=f"https://{HOST}",
        token=TOKEN
    )
    if connections.has_connection("default"):
        print("✅ Successfully connected to Zilliz Cloud!")
    else:
        print("❌ Connection to Zilliz Cloud failed.")
except Exception as e:
    print(f"❌ Error connecting to Zilliz Cloud: {e}") 