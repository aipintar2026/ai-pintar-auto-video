import argparse, json
from engine.production_pipeline import run_pipeline
p=argparse.ArgumentParser(description='AI PINTAR 2.0 staging production')
p.add_argument('--output',default='output_production')
p.add_argument('--publish',action='store_true',help='Requires PUBLISH_ENABLED=true and PUBLISH_DRY_RUN=false; use only after human review')
p.add_argument('--upload-cloudinary',action='store_true',help='Upload to Cloudinary only; no social queue')
p.add_argument('--avatar',default=None,help='Path to approved presenter image or clip')
p.add_argument('--music',default=None,help='Optional licensed music file supplied by user')
p.add_argument('--channel-ids',default='',help='Comma-separated Buffer channel IDs')
a=p.parse_args()
result=run_pipeline(a.output,a.publish,a.avatar,[x.strip() for x in a.channel_ids.split(',') if x.strip()],upload_cloudinary=a.upload_cloudinary,music=a.music)
print(json.dumps(result,ensure_ascii=False,indent=2))
