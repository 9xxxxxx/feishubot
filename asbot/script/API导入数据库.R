library(httr)
library(jsonlite)
library(uuid)
library(tidyverse)
library(RMySQL)
mutate_type <- function(x,y){
  if(!y %in% names(x)) {
    x <- x %>% 
      mutate("{y}" := 0)
  }
  return(x)
}
get_url <- function(api_name,queryid,pageindex,pagesize,isUserQuery,isPreview,paging,conditions){
  extendConditions <- URLencode(conditions,reserved = TRUE)
  reqid <- UUIDgenerate(use.time = TRUE)
  timestamp <-as.character(round(as.numeric(as.POSIXct(now(),tz="CST"))*1000,0))
  key <- "u7BDpKHA6VSqTScpEqZ4cPKmYVbQTAxgTBL2Gtit"
  sign <- toupper(digest::digest(str_c("AS_department",conditions,pageindex,pagesize,paging,reqid,"laifen",timestamp,isPreview,isUserQuery,queryid,key),"sha256", serialize = FALSE))
  url <- str_c("https://ap6-openapi.fscloud.com.cn/t/laifen/open/",
               api_name,
               "?$tenant=laifen&$timestamp=",
               timestamp,
               "&$reqid=",
               reqid,
               "&$appid=AS_department&queryid=",
               queryid,
               "&isUserQuery=",
               isUserQuery,
               "&isPreview=",
               isPreview,
               "&$pageindex=",
               pageindex,
               "&$pagesize=",
               pagesize,
               "&$paging=",
               paging,
               "&$extendConditions=",
               extendConditions,
               "&$sign=",
               sign)
  return(url)
}
get_data <- function(url){
  res <- VERB("GET", url = url)
  a <- fromJSON(content(res, 'text'))
  a_1 <- a[["Data"]][["Entities"]]
  return(a_1)
}
get_list <- function(api_name,queryid,pageindex,pagesize,isUserQuery,isPreview,paging,conditions){
  url <- get_url(api_name,queryid,pageindex,pagesize,isUserQuery,isPreview,paging,conditions)
  res <- VERB("GET", url = url)
  a <- fromJSON(content(res, 'text'))
  a_cnt <- 1:ceiling(a[["Data"]]$TotalRecordCount/5000)
  url_all <- map_chr(a_cnt,~get_url(api_name,queryid,.,pagesize,isUserQuery,isPreview,paging,conditions))
  a_1 <- map_dfr(url_all,get_data)
  return(a_1)
}

a <- get_list("api/vlist/ExecuteQuery",
         "38c53a54-813f-a0e0-0000-06f40ebdeca5",
         "1",
         "5000",
         "true",
         "false",
         "true",
         '[{"name":"new_signedon","val":"not-null","op":"not-null"},{"name":"createdon","val":"before-today","op":"before-today"},{"name":"createdon","val":"60","op":"last-x-days"}]')

a_1 <- a %>%   
  mutate(productmodel_name=pull(new_productmodel_id,name),
         product_name=pull(new_product_id,name),
         applytype=pull(FormattedValues,new_srv_rma_0.new_applytype),
         new_status=new_srv_rma_0.new_status,
         per_name_fenjian=pull(laifen_systemuser2_id,name),
         per_name_yijian=pull(laifen_systemuser_id,name),
         per_name_weixiu=pull(new_srv_workorder_1.new_srv_worker_id,name),
         new_rma_id=pull(new_rma_id,name)
  ) %>% 
  select(new_rma_id,productmodel_name,product_name,laifen_productnumber,new_returnstatus,new_status,applytype,per_name_fenjian,per_name_yijian,per_name_weixiu,new_signedon,new_checkon,laifen_servicecompletetime,laifen_qualityrecordtime,new_deliveriedon) %>% 
  mutate(new_returnstatus=case_when(new_returnstatus==10~"待取件",
                          new_returnstatus==30~"已签收",
                          new_returnstatus==60~"已维修",
                          new_returnstatus==50~"维修中",
                          new_returnstatus==70~"已质检",
                          new_returnstatus==40~"已检测",
                          new_returnstatus==20~"已取件",
                          new_returnstatus==80~"已一检",
                          new_returnstatus==90~"异常",
                          new_returnstatus==100~"一检异常",
                          new_returnstatus==110~"地址异常",
                          TRUE~"X"),
         new_status=case_when(new_status=="10"~"待处理",
                        new_status=="50"~"已评价",
                        new_status=="30"~"已完成",
                        new_status=="40"~"已取消",
                        new_status=="20"~"处理中",
                        new_status=="60"~"已检测",
                        new_status=="80"~"异常",
                        new_status=="70"~"已一检",
                        new_status=="90"~"重复待确认",
                        TRUE~"X"),
         new_signedon=as.POSIXct(str_c(str_sub(new_signedon,1,10)," ",str_sub(new_signedon,12,19))),
         new_checkon=as.POSIXct(str_c(str_sub(new_checkon,1,10)," ",str_sub(new_checkon,12,19))),
         laifen_servicecompletetime=as.POSIXct(str_c(str_sub(laifen_servicecompletetime,1,10)," ",str_sub(laifen_servicecompletetime,12,19))),
         laifen_qualityrecordtime=as.POSIXct(str_c(str_sub(laifen_qualityrecordtime,1,10)," ",str_sub(laifen_qualityrecordtime,12,19))),
         new_deliveriedon=as.POSIXct(str_c(str_sub(new_deliveriedon,1,10)," ",str_sub(new_deliveriedon,12,19)))
         )
conn <- dbConnect(MySQL(),dbname="demo",username="LJH",password="ljhyds666",host="172.16.101.2",port=3306)
dbWriteTable(conn, "maintenance_detail_ruiyun", a_1, overwrite = TRUE,row.names = FALSE)
dbDisconnect(conn)
print("已导入")
