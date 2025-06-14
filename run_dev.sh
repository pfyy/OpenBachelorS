source venv/bin/activate
python3 -m flask --app src/app --debug run -h 127.0.0.1 -p 8443 --extra-files conf/config.json:conf/version.json:conf/assist.json:data/tmpl.json:data/mail.json:data/sandbox_tmpl.json:data/rlv2_tmpl.json:data/crisisV2_tmpl.json:data/rlv2_data.json:data/message.json:data/gacha_pool.json:data/gacha_data.json
