LAMBDA_PACKAGE_NAME=marqo-usage-updater
LAMBDA_SOURCE_DIR=/home/joshua/work/marqo_main/marqo-billing/lambda_package
LAMBDA_DEPENDENCIES_DIR=/home/joshua/work/marqo_main/marqo-billing/lambda_function_deps

# Install dependencies using pip
install_lambda_reqs:
	pip install -r $(LAMBDA_SOURCE_DIR)/requirements.txt --target $(LAMBDA_DEPENDENCIES_DIR)

# Create deployment package zip file
zip_lambda:
	cd $(LAMBDA_DEPENDENCIES_DIR) && zip -r9 ../$(LAMBDA_PACKAGE_NAME).zip .
	cd ..
	cd $(LAMBDA_SOURCE_DIR) && zip -rg ../$(LAMBDA_PACKAGE_NAME).zip ./*
	cd ..

# Clean up
clean:
	rm -rf $(LAMBDA_DEPENDENCIES_DIR)
	rm -f $(LAMBDA_PACKAGE_NAME).zip
	echo "Cleaned."