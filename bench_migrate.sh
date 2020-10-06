
#git reset --hard
#git pull https://github.com/taazurgroup/tailpos_sync.git
cd ../..
bench --site $1 migrate

#cp apps/tailpos_sync/tailpos_sync/public/core/taxes_and_totals.py apps/erpnext/erpnext/controllers/
bench --site $1 clear-cache
bench restart
