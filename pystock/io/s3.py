import boto3


def save_img_to_s3(img_data, key: str):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket("CHART_SAVE_BUCKET_NAME")
    # img_data = compute_sma_and_save_charts_to_s3(stock_df)
    bucket.put_object(Key=key, Body=img_data, ACL="public-read")
    return {"s3_chart_key": key}
