CODREP_NETWORK ?= formatml
CODREP_BBLFSHD_NAME ?= formatml_bblfshd
CODREP_COMMAND ?= ~/.virtualenvs/formatml/bin/python -m formatml codrep
CODREP_DIR ?= .
CODREP_STEPS_DIR ?= $(CODREP_DIR)/steps
CODREP_DATA_DIR ?= $(CODREP_DIR)/outputs
CODREP_CONFIGS_DIR ?= $(CODREP_DIR)/configs
CODREP_ARCHIVE_URL ?= https://github.com/KTH/codrep-2019/archive/master.zip
CODREP_ARCHIVE ?= $(CODREP_DATA_DIR)/master.zip
CODREP_RAW_DIR ?= $(CODREP_DATA_DIR)/raw
CODREP_UASTS_DIR ?= $(CODREP_DATA_DIR)/uasts
CODREP_INSTANCE_ARCHIVE ?= $(CODREP_DATA_DIR)/instance.pickle.bz2
CODREP_TENSORS_DIR ?= $(CODREP_DATA_DIR)/tensors
CODREP_TRAIN_NAME ?= $(shell date '+%Y-%m-%dT%H:%M')
CODREP_TRAIN_DIR ?= $(CODREP_DATA_DIR)/train/$(CODREP_TRAIN_NAME)

bblfshd:
	docker network create $(CODREP_NETWORK) > /dev/null 2>&1 || true
	docker start $(CODREP_BBLFSHD_NAME) > /dev/null 2>&1 \
		|| docker run \
			--detach \
			--rm \
			--name $(CODREP_BBLFSHD_NAME) \
			--network $(CODREP_NETWORK) \
			--privileged \
			--publish 9432:9432 \
			bblfsh/bblfshd:v2.14.0-drivers \
			--log-level DEBUG

download:
	mkdir -p $(CODREP_STEPS_DIR) $(CODREP_DATA_DIR) $(CODREP_CONFIGS_DIR)
	dvc import-url \
		--file $(CODREP_STEPS_DIR)/download.dvc \
		$(CODREP_ARCHIVE_URL) \
		$(CODREP_ARCHIVE)

unzip: download
	dvc run \
		--overwrite-dvcfile \
		--file $(CODREP_STEPS_DIR)/unzip.dvc \
		--deps $(CODREP_ARCHIVE) \
		--outs $(CODREP_RAW_DIR) \
		"unzip $(CODREP_ARCHIVE) \
			&& mv codrep-2019-master/Datasets/learning $(CODREP_RAW_DIR) \
			&& rm -rf codrep-2019-master"

parse: bblfshd unzip
	dvc run \
		--overwrite-dvcfile \
		--file $(CODREP_STEPS_DIR)/parse.dvc \
		--deps $(CODREP_RAW_DIR) \
		--outs $(CODREP_UASTS_DIR) \
		$(CODREP_COMMAND) parse \
			--raw-dir $(CODREP_RAW_DIR) \
			--uasts-dir $(CODREP_UASTS_DIR) \
			--configs-dir $(CODREP_CONFIGS_DIR)

index: parse
	dvc run \
		--overwrite-dvcfile \
		--file $(CODREP_STEPS_DIR)/index.dvc \
		--deps $(CODREP_UASTS_DIR) \
		--outs $(CODREP_INSTANCE_ARCHIVE) \
		$(CODREP_COMMAND) index \
			--uasts-dir $(CODREP_UASTS_DIR) \
			--instance-file $(CODREP_INSTANCE_ARCHIVE) \
			--configs-dir $(CODREP_CONFIGS_DIR) \
			$(CODREP_INDEX_ARGS)

tensorize: index
	dvc run \
		--overwrite-dvcfile \
		--file $(CODREP_STEPS_DIR)/tensorize.dvc \
		--deps $(CODREP_UASTS_DIR) \
		--deps $(CODREP_INSTANCE_ARCHIVE) \
		--outs $(CODREP_TENSORS_DIR) \
		$(CODREP_COMMAND) tensorize \
			--uasts-dir $(CODREP_UASTS_DIR) \
			--instance-file $(CODREP_INSTANCE_ARCHIVE) \
			--tensors-dir $(CODREP_TENSORS_DIR) \
			--configs-dir $(CODREP_CONFIGS_DIR) \
			$(CODREP_TENSORIZE_ARGS)

train: tensorize
	dvc run \
		--overwrite-dvcfile \
		--file $(CODREP_STEPS_DIR)/$(CODREP_TRAIN_NAME)-train.dvc \
		--deps $(CODREP_INSTANCE_ARCHIVE) \
		--deps $(CODREP_TENSORS_DIR) \
		--outs $(CODREP_TRAIN_DIR) \
		$(CODREP_COMMAND) train \
			--instance-file $(CODREP_INSTANCE_ARCHIVE) \
			--tensors-dir $(CODREP_TENSORS_DIR) \
			--train-dir $(CODREP_TRAIN_DIR) \
			--configs-dir $(CODREP_CONFIGS_DIR) \
			$(CODREP_TRAIN_ARGS)

.PHONY: bblfshd download unzip parse index tensorize train
