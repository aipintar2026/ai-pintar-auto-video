import argparse, json
from engine.production import run
p=argparse.ArgumentParser();p.add_argument('--demo-video',action='store_true');p.add_argument('--seed',type=int);args=p.parse_args()
result=run(demo=args.demo_video,seed=args.seed)
print(json.dumps(result,ensure_ascii=False,indent=2))
