#coding=utf-8

DISPLAY_DP = "dp"
DISPLAY_WORDCOUNT = "wordcount"
DISPLAY_CRF = "crf"


#############
# Dict Table#
#############
#[2015.05.17] using new_dict_table for dp . abandon old dict table 
#dict_table = "yinshi_dict"
#[2015.05.13] using new yinshi_dict for word_count based
new_dict_table = "yinshi_dict_new"

################
# Result Table #
################

table_name = "basic_data_new" # dp table name

#[2015.06.08] Add crf result
#[2015.06.10] change to  stat view model 
#crf_result_table_name = "crf_data" 
crf_stat_table_name = "crf_stat_view"

#[2015.05.13] stat_table_name = "stat"
stat_table_name = "stat_view"

###############
# Cache Table #
###############
cache_dp_table_name = "cache"
cache_wordcount_table_name = "cache_dict"
cache_crf_table_name = "cache_crf"