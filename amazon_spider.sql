 ---- qiushi example
CREATE TABLE datahouse.qiushispider (
`eventdate` Date DEFAULT toDate(ctime),
 `username` String,
 `content` String,
 `laugh_count` UInt8,
 `review_count` UInt8,
 `sex` UInt8,
 `age` UInt8,
 `ctime` DateTime DEFAULT now() COMMENT '本地创建时间'
) ENGINE = MergeTree PARTITION BY toYYYYMM(eventdate) ORDER BY (ctime, username) SETTINGS index_granularity = 8192;



CREATE TABLE datahouse.kafka_qiushispider (
`eventdate` Date DEFAULT toDate(ctime),
 `username` String,
 `content` String,
 `laugh_count` UInt8,
 `review_count` UInt8,
 `sex` UInt8,
 `age` UInt8,
 `ctime` DateTime DEFAULT now() COMMENT '本地创建时间'
) ENGINE = Kafka SETTINGS kafka_broker_list = '192.168.5.134:9092', kafka_topic_list = 'qiushispider', kafka_group_name = 'clickhouse', kafka_format = 'JSONEachRow', kafka_skip_broken_messages = 1, kafka_num_consumers = 1;


CREATE MATERIALIZED VIEW datahouse.consumer_qiushispider TO datahouse.qiushispider (
`eventdate` Date DEFAULT toDate(ctime),
 `username` String,
 `content` String,
 `laugh_count` UInt8,
 `review_count` UInt8,
 `sex` UInt8,
 `age` UInt8,
 `ctime` DateTime DEFAULT now()) AS SELECT username,
 content,
 laugh_count,
 review_count,
 sex,
 age FROM datahouse.kafka_qiushispider;


-------- answer spider



CREATE TABLE datahouse.asp_answer (
`country` String,
`question_id`   String,
`ask_date`   String,
`ask_local_date`   String,
`answer_id`   String,
`answer_content`   String,
`answer_author`   String,
`answer_profile_id`   String,
`post_date`   String,
`local_date`   String,
`helpful_count`   String,
`votes`   String,
`add_date_time`  DateTime DEFAULT now() COMMENT '爬取时间'
) ENGINE = MergeTree PARTITION BY toYYYYMM(add_date_time) ORDER BY (add_date_time, question_id) SETTINGS index_granularity = 8192;


CREATE TABLE datahouse.asp_kafka_answer (
`country` String,
`question_id`   String,
`ask_date`   String,
`ask_local_date`   String,
`answer_id`   String,
`answer_content`   String,
`answer_author`   String,
`answer_profile_id`   String,
`post_date`   String,
`local_date`   String,
`helpful_count`   String,
`votes`   String,
`add_date_time`  DateTime DEFAULT now() COMMENT '爬取时间'
) ENGINE = Kafka SETTINGS kafka_broker_list = '192.168.5.134:9092', kafka_topic_list = 'answer', kafka_group_name = 'clickhouse', kafka_format = 'JSONEachRow', kafka_skip_broken_messages = 1, kafka_num_consumers = 1;



CREATE MATERIALIZED VIEW datahouse.consumer_answer TO datahouse.asp_answer (
`country` String,
`question_id`   String,
`ask_date`   String,
`ask_local_date`   String,
`answer_id`   String,
`answer_content`   String,
`answer_author`   String,
`answer_profile_id`   String,
`post_date`   String,
`local_date`   String,
`helpful_count`   String,
`votes`   String,
`add_date_time`  DateTime DEFAULT now() COMMENT '爬取时间') AS SELECT
country,
question_id,
ask_date,
ask_local_date,
answer_id,
answer_content,
answer_author,
answer_profile_id,
post_date,
local_date,
helpful_count,
votes,
add_date_time FROM datahouse.asp_kafka_answer;



-------- question spider


CREATE TABLE datahouse.asp_question (
`country` String,
`asin`   String,
`question_id`   String,
`votes`   String,
`question`   String,
`url`   String,
`answer_count` String,
`add_date_time`      DateTime DEFAULT now() COMMENT '爬取时间'
) ENGINE = MergeTree PARTITION BY toYYYYMM(add_date_time) ORDER BY (add_date_time, question_id) SETTINGS index_granularity = 8192;


CREATE TABLE datahouse.asp_kafka_question (
`country` String,
`asin`   String,
`question_id`   String,
`votes`   String,
`question`   String,
`url`   String,
`answer_count` String,
`add_date_time`      DateTime DEFAULT now() COMMENT '爬取时间'
) ENGINE = Kafka SETTINGS kafka_broker_list = '192.168.5.134:9092', kafka_topic_list = 'question', kafka_group_name = 'clickhouse', kafka_format = 'JSONEachRow', kafka_skip_broken_messages = 1, kafka_num_consumers = 1;



CREATE MATERIALIZED VIEW datahouse.consumer_question TO datahouse.asp_question (
`country` String,
`asin`   String,
`question_id`   String,
`votes`   String,
`question`   String,
`url`   String,
`answer_count` String,
`add_date_time`      DateTime DEFAULT now() COMMENT '爬取时间') AS SELECT
country,
asin,
question_id,
votes,
question,
url,
answer_count,
add_date_time FROM datahouse.asp_kafka_question;


-------- review spider

CREATE TABLE datahouse.asp_review (
`pageurl`  String,
`asin`  String,
`pagetitle`  String,
`review_rating`  String,
`review_title`  String,
`review_title_url`  String,
`author`  String,
`author_linkurl`  String,
`author_profileid`  String,
`classify_asin`  String,
`countrycode`  String,
`review_date`  String,
`local_date`  String,
`w_pro_color`  String,
`verified_purchase`  String,
`review_text`  String,
`w_comments`  String,
`review_votes`  String,
`nowstar`  String,
`review_id`  String,
`w_now`  DateTime DEFAULT now() COMMENT '爬取时间'
) ENGINE = MergeTree PARTITION BY toYYYYMM(w_now) ORDER BY (w_now, asin) SETTINGS index_granularity = 8192;





CREATE TABLE datahouse.asp_kafka_review (
`pageurl`  String,
`asin`  String,
`pagetitle`  String,
`review_rating`  String,
`review_title`  String,
`review_title_url`  String,
`author`  String,
`author_linkurl`  String,
`author_profileid`  String,
`classify_asin`  String,
`countrycode`  String,
`review_date`  String,
`local_date`  String,
`w_pro_color`  String,
`verified_purchase`  String,
`review_text`  String,
`w_comments`  String,
`review_votes`  String,
`nowstar`  String,
`review_id`  String,
`w_now`  DateTime DEFAULT now() COMMENT '爬取时间'
) ENGINE = Kafka SETTINGS kafka_broker_list = '192.168.5.134:9092', kafka_topic_list = 'review', kafka_group_name = 'clickhouse', kafka_format = 'JSONEachRow', kafka_skip_broken_messages = 1, kafka_num_consumers = 1;



CREATE MATERIALIZED VIEW datahouse.consumer_review TO datahouse.asp_review (
`pageurl`  String,
`asin`  String,
`pagetitle`  String,
`review_rating`  String,
`review_title`  String,
`review_title_url`  String,
`author`  String,
`author_linkurl`  String,
`author_profileid`  String,
`classify_asin`  String,
`countrycode`  String,
`review_date`  String,
`local_date`  String,
`w_pro_color`  String,
`verified_purchase`  String,
`review_text`  String,
`w_comments`  String,
`review_votes`  String,
`nowstar`  String,
`review_id`  String,
`w_now`      DateTime DEFAULT now() COMMENT '爬取时间') AS SELECT
pageurl,
asin,
pagetitle,
review_rating,
review_title,
review_title_url,
author,
author_linkurl,
author_profileid,
classify_asin,
countrycode,
review_date,
local_date,
w_pro_color,
verified_purchase,
review_text,
w_comments,
review_votes,
nowstar,
review_id,
w_now FROM datahouse.asp_kafka_review;



-------- bestseller spider
CREATE TABLE datahouse.asp_bestseller (
`country`   String,
`cate_id`   String,
`cate_name`   String,
`cate_url`   String,
`asin`   String,
`ranking`   String,
`pic_url`   String,
`title`   String,
`stars`   String,
`review_counts`   String,
`price`   String,
`add_date_time`      DateTime DEFAULT now() COMMENT '爬取时间'
) ENGINE = MergeTree PARTITION BY toYYYYMM(add_date_time) ORDER BY (add_date_time, cate_name) SETTINGS index_granularity = 8192;


CREATE TABLE datahouse.asp_kafka_bestseller (
`country`   String,
`cate_id`   String,
`cate_name`   String,
`cate_url`   String,
`asin`   String,
`ranking`   String,
`pic_url`   String,
`title`   String,
`stars`   String,
`review_counts`   String,
`price`   String,
`add_date_time`      DateTime DEFAULT now() COMMENT '爬取时间'
) ENGINE = Kafka SETTINGS kafka_broker_list = '192.168.5.134:9092', kafka_topic_list = 'bestseller', kafka_group_name = 'clickhouse', kafka_format = 'JSONEachRow', kafka_skip_broken_messages = 1, kafka_num_consumers = 1;



CREATE MATERIALIZED VIEW datahouse.consumer_bestseller TO datahouse.asp_bestseller (
`country`   String,
`cate_id`   String,
`cate_name`   String,
`cate_url`   String,
`asin`   String,
`ranking`   String,
`pic_url`   String,
`title`   String,
`stars`   String,
`review_counts`   String,
`price`   String,
`add_date_time`      DateTime DEFAULT now() COMMENT '爬取时间') AS SELECT country,
cate_id,
cate_name,
cate_url,
asin,
ranking,
pic_url,
title,
stars,
review_counts,
price,
add_date_time FROM datahouse.asp_kafka_bestseller;


-------- keyword spider

CREATE TABLE datahouse.asp_keyword (
`country`   String,
`url`      String,
`page`      String,
`search_key`      String,
`page_ranking`      String,
`pic_url`      String,
`price`      String,
`product_title`      String,
`product_brand`      String,
`asin`      String,
`is_ad`      String,
`list_id`      String,
`add_date_time`      DateTime DEFAULT now() COMMENT '爬取时间'
) ENGINE = MergeTree PARTITION BY toYYYYMM(add_date_time) ORDER BY (add_date_time, search_key) SETTINGS index_granularity = 8192;


CREATE TABLE datahouse.asp_kafka_keyword (
`country`   String,
`url`      String,
`page`      String,
`search_key`      String,
`page_ranking`      String,
`pic_url`      String,
`price`      String,
`product_title`      String,
`product_brand`      String,
`asin`      String,
`is_ad`      String,
`list_id`      String,
`add_date_time`      DateTime DEFAULT now() COMMENT '爬取时间'
) ENGINE = Kafka SETTINGS kafka_broker_list = '192.168.5.134:9092', kafka_topic_list = 'keyword', kafka_group_name = 'clickhouse', kafka_format = 'JSONEachRow', kafka_skip_broken_messages = 1, kafka_num_consumers = 1;




CREATE MATERIALIZED VIEW datahouse.consumer_keyword TO datahouse.asp_keyword (
`country`   String,
`url`      String,
`page`      String,
`search_key`      String,
`page_ranking`      String,
`pic_url`      String,
`price`      String,
`product_title`      String,
`product_brand`      String,
`asin`      String,
`is_ad`      String,
`list_id`      String,
`add_date_time`      DateTime DEFAULT now() COMMENT '爬取时间') AS SELECT country,
url,
page,
search_key,
page_ranking,
pic_url,
price,
product_title,
product_brand,
asin,
is_ad,
list_id,
add_date_time FROM datahouse.asp_kafka_keyword;



--------  listing spider

drop table asp_listing
drop table asp_kafka_listing
drop table consumer_listing

CREATE TABLE datahouse.asp_listing (
`country` String,
 `asin` String,
 `page_title` String,
 `product_title` String,
 `provide` String,
 `provide_id` String,
 `product_path` String,
 `product_top100_node` String,
 `img1` String,
 `img2` String,
 `img3` String,
 `img4` String,
 `img5` String,
 `price` String,
 `list_price` String,
 `sale_price` String,
 `deal_price` String,
 `price_savings` String,
 `bullet_point1` String,
 `bullet_point2` String,
 `bullet_point3` String,
 `bullet_point4` String,
 `bullet_point5` String,
 `customer_reviews_count` String,
 `ask` String,
 `best_seller` String,
 `best_seller_path` String,
 `stars` String,
 `five_star` String,
 `four_star` String,
 `three_star` String,
 `two_star` String,
 `one_star` String,
 `top_bad_reviews` String,
 `offer_listing` String,
 `soldby` String,
 `soldbyurl` String,
 `fba` String,
 `bsr1` String,
 `bsr1path` String,
 `bsr2` String,
 `bsr2path` String,
 `bsr3` String,
 `bsr3path` String,
 `bsr4` String,
 `bsr4path` String,
 `bsr5` String,
 `bsr5path` String,
 `color` String,
 `color_count` String,
 `product_dimensions` String,
 `item_weight` String,
 `shipping_weight` String,
 `item_model_number` String,
 `issue_date` String,
 `add_date_time` DateTime DEFAULT now() COMMENT '爬取时间'
) ENGINE = MergeTree PARTITION BY toYYYYMM(add_date_time) ORDER BY (add_date_time, asin) SETTINGS index_granularity = 8192;


CREATE TABLE datahouse.asp_kafka_listing (
`country` String,
 `asin` String,
 `page_title` String,
 `product_title` String,
 `provide` String,
 `provide_id` String,
 `product_path` String,
 `product_top100_node` String,
 `img1` String,
 `img2` String,
 `img3` String,
 `img4` String,
 `img5` String,
 `price` String,
 `list_price` String,
 `sale_price` String,
 `deal_price` String,
 `price_savings` String,
 `bullet_point1` String,
 `bullet_point2` String,
 `bullet_point3` String,
 `bullet_point4` String,
 `bullet_point5` String,
 `customer_reviews_count` String,
 `ask` String,
 `best_seller` String,
 `best_seller_path` String,
 `stars` String,
 `five_star` String,
 `four_star` String,
 `three_star` String,
 `two_star` String,
 `one_star` String,
 `top_bad_reviews` String,
 `offer_listing` String,
 `soldby` String,
 `soldbyurl` String,
 `fba` String,
 `bsr1` String,
 `bsr1path` String,
 `bsr2` String,
 `bsr2path` String,
 `bsr3` String,
 `bsr3path` String,
 `bsr4` String,
 `bsr4path` String,
 `bsr5` String,
 `bsr5path` String,
 `color` String,
 `color_count` String,
 `product_dimensions` String,
 `item_weight` String,
 `shipping_weight` String,
 `item_model_number` String,
 `issue_date` String,
 `add_date_time` DateTime DEFAULT now()
) ENGINE = Kafka SETTINGS kafka_broker_list = '192.168.5.134:9092', kafka_topic_list = 'listing', kafka_group_name = 'clickhouse', kafka_format = 'JSONEachRow', kafka_skip_broken_messages = 1, kafka_num_consumers = 1;



CREATE MATERIALIZED VIEW datahouse.consumer_listing TO datahouse.asp_listing (
`country` String,
 `asin` String,
 `page_title` String,
 `product_title` String,
 `provide` String,
 `provide_id` String,
 `product_path` String,
 `product_top100_node` String,
 `img1` String,
 `img2` String,
 `img3` String,
 `img4` String,
 `img5` String,
 `price` String,
 `list_price` String,
 `sale_price` String,
 `deal_price` String,
 `price_savings` String,
 `bullet_point1` String,
 `bullet_point2` String,
 `bullet_point3` String,
 `bullet_point4` String,
 `bullet_point5` String,
 `customer_reviews_count` String,
 `ask` String,
 `best_seller` String,
 `best_seller_path` String,
 `stars` String,
 `five_star` String,
 `four_star` String,
 `three_star` String,
 `two_star` String,
 `one_star` String,
 `top_bad_reviews` String,
 `offer_listing` String,
 `soldby` String,
 `soldbyurl` String,
 `fba` String,
 `bsr1` String,
 `bsr1path` String,
 `bsr2` String,
 `bsr2path` String,
 `bsr3` String,
 `bsr3path` String,
 `bsr4` String,
 `bsr4path` String,
 `bsr5` String,
 `bsr5path` String,
 `color` String,
 `color_count` String,
 `product_dimensions` String,
 `item_weight` String,
 `shipping_weight` String,
 `item_model_number` String,
 `issue_date` String,
 `add_date_time` DateTime DEFAULT now()) AS SELECT country,
 asin,
 page_title,
 product_title,
 provide,
 provide_id,
 product_path,
 product_top100_node,
 img1,
 img2,
 img3,
 img4,
 img5,
 price,
 list_price,
 sale_price,
 deal_price,
 price_savings,
 bullet_point1,
 bullet_point2,
 bullet_point3,
 bullet_point4,
 bullet_point5,
 customer_reviews_count,
 ask,
 best_seller,
 best_seller_path,
 stars,
 five_star,
 four_star,
 three_star,
 two_star,
 one_star,
 top_bad_reviews,
 offer_listing,
 soldby,
 soldbyurl,
 fba,
 bsr1,
 bsr1path,
 bsr2,
 bsr2path,
 bsr3,
 bsr3path,
 bsr4,
 bsr4path,
 bsr5,
 bsr5path,
 color,
 color_count,
 product_dimensions,
 item_weight,
 shipping_weight,
 item_model_number,
 issue_date,
 add_date_time FROM datahouse.asp_kafka_listing;








