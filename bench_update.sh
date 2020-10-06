
#git reset --hard
cd ../..
bench update

#cp apps/tailpos_sync/tailpos_sync/public/core/taxes_and_totals.py apps/erpnext/erpnext/controllers/
bench --site $1 clear-cache
bench restart
