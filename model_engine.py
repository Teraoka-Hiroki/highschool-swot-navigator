"""
model_engine.py
高校生のための自己SWOTクロス分析 4段階逐次推論エンジン
前置き・箇条書きを一切排除し、2〜3文のアドバイス本文のみを確実に完結生成
"""

import os
import re
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# CPUコアをフル活用
if torch.get_num_threads() < 4:
    torch.set_num_threads(4)

MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"

class SWOTAnalyzer:
    def __init__(self, model_name=MODEL_NAME):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None

    def load(self):
        """モデルとトークナイザーをロード"""
        if self.tokenizer is None or self.model is None:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                dtype=torch.bfloat16,
                device_map="cpu"
            )
            self.model.eval()

    def generate_single_strategy(self, strategy_name: str, factor_a_label: str, factor_a_val: str, factor_b_label: str, factor_b_val: str, direction_guide: str) -> str:
        """1つの象限の戦略を確実に最後まで完結させて生成"""
        self.load()

        system_prompt = (
            "あなたは高校生の自律的な探究学習とキャリア形成を支えるプロの進路メンターです。"
            "挨拶や前置き、箇条書き、見出しは絶対に書かず、高校生への具体的で前向きなアドバイス本文のみを、2〜3文の完結した美しい日本語で直接出力してください。"
        )

        user_prompt = (
            f"【分析データ】\n"
            f"- {factor_a_label}: {factor_a_val}\n"
            f"- {factor_b_label}: {factor_b_val}\n\n"
            f"【戦略テーマ】\n"
            f"{strategy_name}\n"
            f"方針: {direction_guide}\n\n"
            f"※前置きや箇条書き、見出し（**〜**など）は一切書かず、2〜3文のアドバイス本文だけを出力してください。"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        model_inputs = self.tokenizer([text], return_tensors="pt").to("cpu")

        with torch.no_grad():
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=350,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
                do_sample=True
            )

        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

        # クリーンアップ（念のための不要記号除去）
        response = re.sub(r'^(?:【.*?】|\*\*.*?\*\*|#+.*?)\s*', '', response).strip()
        response = re.sub(r'^[（\(].*?[）\)]\s*', '', response).strip()
        response = re.sub(r'^\*\*(?:内|目的|方針|戦略)\s*[:：]\*\*\s*', '', response).strip()

        # 万が一途中で切れていた場合、最後の「。」までで綺麗に完結させる
        if "。" in response:
            last_period_idx = response.rfind("。")
            response = response[:last_period_idx + 1]

        return response
