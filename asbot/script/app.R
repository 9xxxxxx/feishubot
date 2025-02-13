library(shiny)
library(bs4Dash)
library(tidyverse)
library(RODBC)
library(echarts4r)
library(DT)
library(shinyWidgets)
library(htmlwidgets)
library(RMySQL)
library(shinyjs)
conn <- dbConnect(MySQL(),dbname="demo",username="LJH",password="ljhyds666",host="172.16.101.2",port=3306)
dt <- dbGetQuery(conn,"select * from maintenance_detail_ruiyun where productmodel_name in ('产成品-吹风机','产成品-电动牙刷')") %>% 
  mutate(across(new_signedon:new_deliveriedon,as.POSIXct))
dbDisconnect(conn)
# dt_fenjian <- dbGetQuery(conn,"
# select *
# from maintenance_detail_ruiyun
# where new_checkon is not null
# 	and date_format(new_checkon,'%Y-%m-%d') >= date_sub(date_format(now(),'%Y-%m-%d'),interval 28 day)
# 	and new_returnstatus <> '异常'
# 	and new_status <> '已取消'")
KPI <- data.frame(分拣组人效=300,
                  分拣组时效达成率=0.96,
                  分拣组时效=12,
                  寄修组人效=1,
                  维修人效=1,
                  质检人效=1,
                  发货人效=1,
                  寄修组吹风机人效=55,
                  寄修组电动牙刷人效=100,
                  寄修组时效达成率=0.98,
                  寄修组时效=60,
                  维修时效达成率=0.97,
                  质检时效达成率=0.98,
                  发货时效达成率=0.98,
                  维修时效=36,
                  质检时效=14,
                  发货时效=10,
                  异常倍数=3,
                  日均剔除=100,
                  人效剔除_上限=300,
                  人效剔除_下限=10
                  )

box_date_s <- floor_date(as.POSIXct(today()-1), "month")-months(1)
box_date_e <- as.POSIXct(today())
filter_fun <- function(x,c1,c2,d1,d2,f1,f2,f3,kpi,kpi1,n1){
  a <- x %>% 
    rename("new_time_2":=!!c2,"new_time_1":=!!c1) %>% 
    filter(!is.na(new_time_2),
           between(new_time_2,d1,d2),
           !new_returnstatus %in% f1,
           !new_status %in% f2,
           applytype %in% f3) %>% 
    mutate(时长_小时=as.numeric(difftime(new_time_2,new_time_1,units = "hours")),
           时效类型=if_else(时长_小时<=kpi[1,kpi1],"完成",if_else(时长_小时<=(kpi$异常倍数[1]*kpi[1,kpi1]),"未完成","异常")),
           ds=as.POSIXct(format(new_time_2,format="%Y/%m/%d"))) %>% 
    rename(!!c2:="new_time_2",!!c1:="new_time_1",!!n1:="时长_小时")
  return(a)
}
gbd_fun <- function(x,c2,p1,kpi,kpi1,n1){
  if(p1==''){
    a <- x %>% 
      rename("new_time_2":=!!c2,"时长_小时":=!!n1) %>% 
      group_by(ds) %>% 
      summarise(业务量=n(),
                人数=1,
                人效=业务量/人数,
                人效达成率=人效/kpi[1,kpi1],
                时效=sum(时长_小时,na.rm = TRUE),
                单均时效=时效/业务量,
                时效达成单数=sum(if_else(时效类型=="完成",1,0),na.rm = TRUE),
                时效单数=sum(if_else(时效类型%in%c("完成","未完成"),1,0),na.rm = TRUE),
                时效达成率=时效达成单数/时效单数,
                .groups = "drop") %>% 
      mutate(mon=year(ds)*100+month(ds),dy=day(ds),日均业务量=if_else(业务量>=kpi[1,"日均剔除"],业务量,NA))
  } else {
    a <- x %>% 
      rename("new_time_2":=!!c2,"per_name":=!!p1,"时长_小时":=!!n1) %>% 
      group_by(ds,per_name) %>% 
      mutate(per_n=n()) %>% 
      ungroup() %>% 
      group_by(ds) %>% 
      summarise(业务量=n(),
                业务量_不含流水线=sum(if_else(per_n<kpi[1,"人效剔除_上限"]&per_n>kpi[1,"人效剔除_下限"],1,0)),
                人数=n_distinct(if_else(per_n<kpi[1,"人效剔除_上限"]&per_n>kpi[1,"人效剔除_下限"],per_name,NA),na.rm = TRUE),
                人效=业务量_不含流水线/人数,
                人效达成率=人效/kpi[1,kpi1],
                时效=sum(时长_小时,na.rm = TRUE),
                单均时效=时效/业务量,
                时效达成单数=sum(if_else(时效类型=="完成",1,0),na.rm = TRUE),
                时效单数=sum(if_else(时效类型%in%c("完成","未完成"),1,0),na.rm = TRUE),
                时效达成率=时效达成单数/时效单数,
                .groups = "drop") %>% 
      mutate(mon=year(ds)*100+month(ds),dy=day(ds),日均业务量=if_else(业务量>=kpi[1,"日均剔除"],业务量,NA))
  }
  return(a)
}
gbd_all_fun <- function(x,n1){
  a <- x %>% 
    filter(dy<=day(today()-1)) %>% 
    group_by(mon) %>% 
    summarise(总业务量=round(sum(业务量),0),日均业务量=round(mean(日均业务量,na.rm = TRUE),1),人效=round(总业务量/sum(人数),1),人效达成率=人效/KPI[1,n1],单均时效=round(sum(时效)/总业务量,1),时效达成率=sum(时效达成单数)/sum(时效单数),.groups = "drop") %>% 
    rename(!!n1:="人效")
  a <- rbind(a,(a[2,]/a[1,])-1)
  return(a)
}


###分拣数据处理
dt_fenjian <- filter_fun(dt,"new_signedon","new_checkon",box_date_s,box_date_e,c('异常'),c('已取消'),c("换货","寄修/返修","退货"),KPI,"分拣组时效","分拣时长_小时")
dt_fenjian_gbd <- gbd_fun(dt_fenjian,"new_checkon","per_name_fenjian",KPI,"分拣组人效","分拣时长_小时")
dt_fenjian_gbd_all <- gbd_all_fun(dt_fenjian_gbd,"分拣组人效")



####寄修数据处理
dt_weixiu <- filter_fun(dt,"new_checkon","laifen_servicecompletetime",box_date_s,box_date_e,c('异常','一检异常'),c('已取消'),c("寄修/返修"),KPI,"维修时效","维修时长_小时")
dt_weixiu_gbd <- gbd_fun(dt_weixiu,"laifen_servicecompletetime","per_name_weixiu",KPI,"维修人效","维修时长_小时")
dt_weixiu_gbdp <- dt_weixiu %>% 
  group_by(ds,per_name_weixiu) %>% 
  mutate(per_n=n()) %>% 
  ungroup() %>% 
  group_by(ds,productmodel_name) %>% 
  summarise(业务量=n(),
            业务量_不含流水线=sum(if_else(per_n<KPI[1,"人效剔除_上限"]&per_n>KPI[1,"人效剔除_下限"],1,0)),
            人数=n_distinct(if_else(per_n<KPI[1,"人效剔除_上限"]&per_n>KPI[1,"人效剔除_下限"],per_name_weixiu,NA),na.rm = TRUE),
            人效=业务量_不含流水线/人数,
            时效=sum(维修时长_小时,na.rm = TRUE),
            单均时效=时效/业务量,
            时效达成单数=sum(if_else(时效类型=="完成",1,0),na.rm = TRUE),
            时效单数=sum(if_else(时效类型%in%c("完成","未完成"),1,0),na.rm = TRUE),
            时效达成率=时效达成单数/时效单数,
            .groups = "drop") %>% 
  mutate(mon=year(ds)*100+month(ds),
         dy=day(ds),
         人效达成率=人效/if_else(productmodel_name=="产成品-吹风机",KPI$寄修组吹风机人效[1],KPI$寄修组电动牙刷人效[1]))


dt_zhijian <- filter_fun(dt,"laifen_servicecompletetime","laifen_qualityrecordtime",box_date_s,box_date_e,c('异常','一检异常'),c('已取消'),c("寄修/返修"),KPI,"质检时效","质检时长_小时")
dt_zhijian_gbd <- gbd_fun(dt_zhijian,"laifen_qualityrecordtime","",KPI,"质检人效","质检时长_小时")

dt_fahuo <- filter_fun(dt,"laifen_qualityrecordtime","new_deliveriedon",box_date_s,box_date_e,c('异常','一检异常'),c('已取消'),c("寄修/返修"),KPI,"发货时效","发货时长_小时")
dt_fahuo_gbd <- gbd_fun(dt_fahuo,"new_deliveriedon","",KPI,"发货人效","发货时长_小时")

dt_jixiu <- filter_fun(dt,"new_checkon","new_deliveriedon",box_date_s,box_date_e,c('异常','一检异常'),c('已取消'),c("寄修/返修"),KPI,"寄修组时效","寄修时长_小时")
dt_jixiu_gbd <- gbd_fun(dt_jixiu,"new_deliveriedon","",KPI,"寄修组人效","寄修时长_小时") %>% 
  select(-人数,-人效,-人效达成率) %>% 
  left_join(select(filter(dt_weixiu_gbdp,productmodel_name=="产成品-吹风机"),ds,业务量,人数,人效,人效达成率,业务量_不含流水线),by=c("ds"="ds"),suffix=c("_寄修","")) %>% 
  left_join(select(filter(dt_weixiu_gbdp,productmodel_name=="产成品-电动牙刷"),ds,业务量,人数,人效,人效达成率,业务量_不含流水线),by=c("ds"="ds"),suffix=c("_风机","_牙刷")) %>% 
  left_join(select(dt_weixiu_gbd,ds,时效达成单数,时效单数,时效达成率),by=c("ds"="ds"),suffix=c("_寄修","")) %>% 
  left_join(select(dt_zhijian_gbd,ds,时效达成单数,时效单数,时效达成率),by=c("ds"="ds"),suffix=c("_维修","")) %>%
  left_join(select(dt_fahuo_gbd,ds,时效达成单数,时效单数,时效达成率),by=c("ds"="ds"),suffix=c("_质检","_发货"))
dt_jixiu_gbd_all <- dt_jixiu_gbd %>% 
  filter(dy<=day(today()-1)) %>% 
  group_by(mon) %>% 
  summarise(总业务量=sum(业务量_寄修),日均业务量=mean(日均业务量,na.rm = TRUE),时效达成率=sum(时效达成单数_寄修)/sum(时效单数_寄修),风机人效达成率=sum(业务量_不含流水线_风机)/sum(人数_风机)/KPI$寄修组吹风机人效[1],牙刷人效达成率=sum(业务量_不含流水线_牙刷)/sum(人数_牙刷)/KPI$寄修组电动牙刷人效[1],维修时效达成率=sum(时效达成单数_维修)/sum(时效单数_维修),质检时效达成率=sum(时效达成单数_质检)/sum(时效单数_质检),发货时效达成率=sum(时效达成单数_发货)/sum(时效单数_发货))
dt_jixiu_gbd_all <- rbind(dt_jixiu_gbd_all,(dt_jixiu_gbd_all[2,]/dt_jixiu_gbd_all[1,])-1)

##########################
percent_string <- function(name,x,y){
  a <- if_else(name=="",str_c(round(x,y)*100,"%"),str_c(name,": ",round(x,y)*100,"%"))
  return(a)
}

valueBoxSpark <- function(value, title, sparkobj = NULL,  subtitle,subtitle2,info = NULL, info_show ,
                          icon = NULL, color = "aqua", width = 4, href = NULL){
  
  if (!is.null(icon))
    shinydashboard:::tagAssert(icon, type = "i")
  info_icon <- tags$small(
    tags$i(
      class = "fa fa-info-circle fa-lg",
      title = info,
      `data-toggle` = "tooltip",
      style = "color: white;"
    ),
    class = "pull-right float-right"
  )
  
  boxContent <- div(
    class = paste0("small-box bg-", color),
    div(
      class = "inner",
      tags$small(title),
      if (info_show) info_icon,
      h3(value),
      if (!is.null(sparkobj)) sparkobj,
      p(subtitle),
      p(subtitle2),
      style = str_c("background-color: ",color,";color: white;")
    ),
    if (!is.null(icon)) div(class = "icon-large icon", icon, style = "z-index; 0")
  )
  
  if (!is.null(href)) 
    boxContent <- a(href = href, boxContent)
  
  div(
    boxContent
  )
}
box_chart <- function(dt,x,y){
  chart <- dt %>%
    group_by(mon) %>% 
    e_charts_(x,height = 100) %>%
    e_line_(y) %>%
    e_legend(show=FALSE) %>%
    e_y_axis(show=FALSE) %>% 
    e_x_axis(show=FALSE) %>%
    e_color(color=c("grey","white"),background = "rgba(0,0,0,0)") %>% 
    e_grid(left="2%",right="2%",top="2%", height = "90%",bottom="2%") %>% 
    e_tooltip(trigger = "item")
  return(chart)
}

gbp_fun <- function(x,p1,kpi,n1){
    a <- x %>% 
      rename("per_name":=!!p1,"时长_小时":=!!n1) %>% 
      group_by(ds,per_name,productmodel_name) %>% 
      summarise(业务量=n(),
                时效=sum(时长_小时,na.rm = TRUE),
                单均时效=时效/业务量,
                时效达成单数=sum(if_else(时效类型=="完成",1,0),na.rm = TRUE),
                时效单数=sum(if_else(时效类型%in%c("完成","未完成"),1,0),na.rm = TRUE),
                时效达成率=时效达成单数/时效单数,
                .groups = "drop") %>% 
      mutate(mon=year(ds)*100+month(ds),dy=day(ds),日均业务量=if_else(业务量>=kpi[1,"日均剔除"],业务量,NA))
  return(a)
}
dt_weixiu_gbp <- gbp_fun(dt_weixiu,"per_name_weixiu",KPI,"维修时长_小时")

line_chart_per <- function(dt,x,y){
  chart <- dt %>%
    filter(业务量<KPI[1,"人效剔除_上限"]&业务量>KPI[1,"人效剔除_下限"]) %>% 
    group_by(per_name) %>% 
    e_charts_(x) %>%
    e_line_(y,symbolSize=htmlwidgets::JS(
      "function(value){return value[1]/10}"
    )) %>% 
    e_tooltip(trigger = "item") %>% 
    e_datazoom(type = "slider")
  return(chart)
}
#box_chart(dt_fenjian_gbd,"dy","业务量")
#line_chart_per(dt_weixiu_gbp,"ds","业务量")
box_out <- function(dt_,x,y,value1,value2,value3,e,color,updown){
  vb <- valueBoxSpark(
    value = value1,
    title = toupper(y),
    sparkobj = box_chart(dt_,x,y),
    subtitle = tagList(HTML(updown), value2),
    subtitle2 = tagList(value3),
    info = NULL,
    info_show = if_else(updown=="&darr;",TRUE,FALSE),
    icon = icon(e),
    width = 2,
    color = color,
    href = NULL
  )
  return(vb)
}


th_dis_title <- function(dt,dt_sum,abc,kpi,z){
  for (i in 1:nrow(abc)) {
    if(abc[i,4]=="round"){
      dt[1,abc[i,1]] <- round(dt_sum[1,abc[i,2]]/dt_sum[1,abc[i,3]],1)
    }else if(abc[i,4]=="percent"){
      dt[,abc[i,1]] <- as.character(dt[,abc[i,1]])
      dt[1,abc[i,1]] <- percent_string("",dt_sum[1,abc[i,2]]/dt_sum[1,abc[i,3]],3)
    }else if(abc[i,4]=="mean"){
      dt[1,abc[i,1]] <- dt[1,abc[i,2]]
    }else{
      dt[,abc[i,1]] <- as.character(dt[,abc[i,1]])
      dt[1,abc[i,1]] <- percent_string("",dt_sum[1,abc[i,2]]/dt_sum[1,abc[i,3]]/kpi[1,abc[i,4]],3)
    }
  }
  z_ <- z+1
  return(as.character(dt[1,z_]))
}

# a_sum <- dt_fenjian_gbd %>%
#    summarise(across(where(is.numeric),sum,na.rm=TRUE))
# a_mean <- dt_fenjian_gbd %>%
#   summarise(across(where(is.numeric),mean,na.rm=TRUE))
# test <- th_dis_title(a_mean,a_sum,summa_mean_fenjian,KPI,c(-3,-7))
# test <- th_dis_title(a_sum,a_sum,summa_sum_fenjian,KPI,c(-3,-7))

summa_sum_fenjian <- data.frame(a=c(4,5,7,10),b=c(1,1,6,8),c=c(3,3,1,9),d=c("round","分拣组人效","round","percent"))
summa_mean_fenjian <- data.frame(a=c(1,4,5,7,10),b=c(13,1,1,6,8),c=c(13,3,3,1,9),d=c("mean","round","分拣组人效","round","percent"))
summa_sum_jixiu <- data.frame(a=c(3,6,12,13,17,18,22,25,28),b=c(2,4,14,14,19,19,20,23,26),c=c(1,5,11,11,16,16,21,24,27),d=c("round","percent","round","寄修组吹风机人效","round","寄修组电动牙刷人效","percent","percent","percent"))
summa_mean_jixiu <- data.frame(a=c(1,3,6,12,13,17,18,22,25,28),b=c(9,2,4,14,14,19,19,20,23,26),c=c(9,1,5,11,11,16,16,21,24,27),d=c("mean","round","percent","round","寄修组吹风机人效","round","寄修组电动牙刷人效","percent","percent","percent"))
summa_sum_weixiu_fenji <- data.frame(a=c(4,6,9,12),b=c(2,5,7,2),c=c(3,1,8,3),d=c("round","round","percent","寄修组吹风机人效"))
summa_sum_weixiu_yashuai <- data.frame(a=c(4,6,9,12),b=c(2,5,7,2),c=c(3,1,8,3),d=c("round","round","percent","寄修组电动牙刷人效"))
summa_sum_zhijian <- data.frame(a=c(6,9),b=c(5,7),c=c(1,8),d=c("round","percent"))
summa_mean_zhijian <- data.frame(a=c(1,6,9),b=c(12,5,7),c=c(12,1,8),d=c("mean","round","percent"))


th_dis <- function(x,y1,y2,z){
  a_sum <- x %>% 
    summarise(across(where(is.numeric),sum,na.rm=TRUE))
  a_sum_2 <- c("总计",th_dis_title(a_sum,a_sum,y1,KPI,z))
  a_mean <- x %>% 
    summarise(across(where(is.numeric),mean,na.rm=TRUE)) %>% 
    mutate(across(where(is.numeric),round,1))
  a_mean_2 <- c("平均",th_dis_title(a_mean,a_sum,y2,KPI,z))
  a_names <- names(x[,z])
  sketch <- htmltools::withTags(table(
    class='display',
    thead(
      tr(
        lapply(a_names,th)
      ),
      tr(
        lapply(a_sum_2,th)
      ),
      tr(
        lapply(a_mean_2,th)
      )
    )
  ))
  return(sketch)
}



dt_out <- function(dt,col,x1,x2,y,round,percent){
  dt_ <- dt %>% 
    mutate(ds=as.character(ds))
  datatable(dt_[,y],
            extensions = 'Buttons',
            selection = 'single',
            style = "bootstrap4",
            rownames = FALSE,
            container = th_dis(dt_,x1,x2,y),
            options = list(
              scrollX = TRUE,
              pageLength = 60,
              fixedColumns = list(leftColumns = col),
              columnDefs = list(
                list(targets = c(1:ncol(dt_[,y])-1), className = 'dt-nowrap')
              ),
              dom = 'Btip',
              extensions = 'Buttons', 
              buttons = c('csv', 'excel')
            )
  ) %>% 
    formatRound(round, 1) %>%
    formatPercentage(percent, 1)
}

# formatStyle_map <- function(a,b){
#   formatStyle(columns = a,
#               background = styleColorBar(c(0,1,dt_fenjian_gbd[a]), b),
#               backgroundSize = '98% 80%',
#               backgroundRepeat = 'no-repeat',
#               backgroundPosition = 'center')
# }
# test <- dt_jixiu_gbd[,c(-3,-6,-8,-9,-10,-12,-15,-17,-20,-22,-25,-28)]
# dt_out(dt_jixiu_gbd,1,summa_sum_jixiu,summa_mean_jixiu,c(-3,-6,-8,-9,-10,-12,-15,-17,-20,-22,-25,-28))
#dt_out(dt_jixiu_gbd,1,summa_sum_jixiu,summa_mean_jixiu,c(-3,-6,-8,-9,-10,-12,-15,-17,-20,-22,-25,-28),c(3,7,10),c(5,8,11,13,15,17))
# dt_out(dt_zhijian_gbd,1,summa_sum_zhijian,summa_mean_zhijian,c(-3,-4,-5,-6,-9,-11,-12,-13),c(3),c(5)) %>%
#   formatStyle(columns = 2,
#               background = styleColorBar(dt_zhijian_gbd[2], '#fbb8a8'),
#               backgroundSize = '98% 80%',
#               backgroundRepeat = 'no-repeat',
#               backgroundPosition = 'left')
loginpage <- div(id = "loginpage", style = "width: 500px; max-width: 100%; margin: 0 auto; padding: 20px;",
                 wellPanel(
                   tags$h2("LOG IN", class = "text-center", style = "padding-top: 0;color:#333; font-weight:600;"),
                   textInput("userName", placeholder="Username", label = tagList(icon("user"), "Username")),
                   passwordInput("passwd", placeholder="Password", label = tagList(icon("unlock-alt"), "Password")),
                   br(),
                   div(
                     style = "text-align: center;",
                     actionButton("login", "SIGN IN", style = "color: white; background-color:#3c8dbc;
                                 padding: 10px 15px; width: 150px; cursor: pointer;
                                 font-size: 18px; font-weight: 600;"),
                     shinyjs::hidden(
                       div(id = "nomatch",
                           tags$p("Oops! Incorrect username or password!",
                                  style = "color: red; font-weight: 600; 
                                            padding-top: 5px;font-size:16px;", 
                                  class = "text-center"))),
                     # br(),
                     # br(),
                     # tags$code("Username: myuser  Password: mypass"),
                     # br(),
                     # tags$code("Username: myuser1  Password: mypass1")
                   ))
)

credentials = data.frame(
  username_id = c("laifen", "myuser"),
  passod   = c("laifen666", "mypass1")
)

header <- dashboardHeader( title = "laifen Dashboard", fixed=TRUE,tags$style("div.form-group.shiny-input-container {margin-top: 16px;margin-left: 16px;}"),uiOutput("logoutbtn"),awesomeCheckbox(inputId = "sidebar_close",
                                                                                                        label = "Sidebar",
                                                                                                        value = TRUE,
                                                                                                        status = "default"))

sidebar <- bs4DashSidebar(id = "sidebar",
                          skin = "light",
                          status = "blue",
                          elevation = 3,
                          disable = FALSE,
                          collapsed = TRUE,
                          uiOutput("sidebarpanel")) 
body <- bs4DashBody(shinyjs::useShinyjs(), uiOutput("body"))
ui <- bs4DashPage(header, sidebar, body, skin = "blue")
# Define server logic required to draw a histogram
server <- function(input, output,session){
  login = FALSE
  USER <- reactiveValues(login = login)
  
  observe({ 
    if (USER$login == FALSE) {
      if (!is.null(input$login)) {
        if (input$login > 0) {
          Username <- isolate(input$userName)
          Password <- isolate(input$passwd)
          if(length(which(credentials$username_id==Username))==1) { 
            pasmatch  <- credentials["passod"][which(credentials$username_id==Username),]
            pasverify <- if_else(pasmatch==Password,TRUE,FALSE)
            if(pasverify) {
              USER$login <- TRUE
            } else {
              shinyjs::toggle(id = "nomatch", anim = TRUE, time = 1, animType = "fade")
              shinyjs::delay(3000, shinyjs::toggle(id = "nomatch", anim = TRUE, time = 1, animType = "fade"))
            }
          } else {
            shinyjs::toggle(id = "nomatch", anim = TRUE, time = 1, animType = "fade")
            shinyjs::delay(3000, shinyjs::toggle(id = "nomatch", anim = TRUE, time = 1, animType = "fade"))
          }
        } 
      }
    }    
  })
  
  output$logoutbtn <- renderUI({
    req(USER$login)
    tags$li(a(icon("sign-out"), "Logout", 
              href="javascript:window.location.reload(true)"),
            class = "dropdown", 
            style = "background-color: #eee !important; border: 0;
                    font-weight: bold; margin:5px; padding: 10px;")
    
  })
  
  output$sidebarpanel <- renderUI({
    if (USER$login == TRUE ){ 
      sidebarMenu(
        id = "sidebarMenu",
        menuItem(
          "分拣组",
          tabName = "item1",
          icon = icon("layer-group")
        ),
        menuItem(
          "寄修组",
          tabName = "item2",
          icon = icon("cart-shopping")
        )
      )
    }
  })
  
  output$body <- renderUI({
    if (USER$login == TRUE ) {
      tabItems(
        tabItem(
          tabName = "item1",
          class = "active",
          fluidRow(
            valueBoxOutput("vbox",width = 2),
            valueBoxOutput("vbox2",width = 2),
            valueBoxOutput("vbox3",width = 2),
            valueBoxOutput("vbox4",width = 2),
            valueBoxOutput("vbox5",width = 2),
            valueBoxOutput("vbox6",width = 2)
          ),
          tags$hr(),
          fluidRow(
            tabBox(
              width = 12,
              title=NULL,
              tabPanel("总计",
                       fluidRow(
                         column(width = 3,
                                airDatepickerInput(
                                  inputId = "check_on_select3",
                                  value=c(floor_date(as.POSIXct(today()-1), "month"),as.POSIXct(today()-1)),
                                  label = "检测日期:",
                                  range = TRUE,
                                  placeholder = NULL,
                                  multiple = 5, 
                                  clearButton = TRUE
                                )
                         ),
                         column(width = 3,
                                virtualSelectInput(
                                  inputId = "product_name_select3",
                                  label = "产品类型:",
                                  choices = c("产成品-电动牙刷","产成品-吹风机"),
                                  selected = "产成品-吹风机",
                                  showValueAsTags = TRUE,
                                  search = TRUE,
                                  multiple = TRUE
                                )
                         ),
                         column(width = 3,
                                virtualSelectInput(
                                  inputId = "bar_metric_fenjian",
                                  label = "选择柱形图指标：",
                                  choices = c("业务量","人效","单均时效"),
                                  selected = "业务量",
                                  showValueAsTags = TRUE,
                                  search = TRUE,
                                  multiple = FALSE
                                )
                         ),
                         column(width = 3,
                                virtualSelectInput(
                                  inputId = "line_metric_fenjian",
                                  label = "选择折线图指标：",
                                  choices = c("人效达成率", "时效达成率"),
                                  selected = "时效达成率",
                                  showValueAsTags = TRUE,
                                  search = TRUE,
                                  multiple = TRUE
                                )
                         )
                       ),
                       fluidRow(
                         column(
                           width = 12,
                           echarts4rOutput("combo_chart_fenjian")
                         )
                       ),
                       fluidRow(
                         column(width = 12,
                                DTOutput('dt_fenjian_ui3')
                         )
                       )
              ),
              tabPanel("寄修",
                       fluidRow(
                         column(width = 6,
                                airDatepickerInput(
                                  inputId = "check_on_select",
                                  value=c(floor_date(as.POSIXct(today()-1), "month"),as.POSIXct(today()-1)),
                                  label = "检测日期:",
                                  range = TRUE,
                                  placeholder = NULL,
                                  multiple = 5, 
                                  clearButton = TRUE
                                )
                         ),
                         column(width = 6,
                                virtualSelectInput(
                                  inputId = "product_name_select",
                                  label = "产品类型:",
                                  choices = c("产成品-电动牙刷","产成品-吹风机"),
                                  selected = "产成品-吹风机",
                                  showValueAsTags = TRUE,
                                  search = TRUE,
                                  multiple = TRUE
                                )
                         )
                       ),
                       fluidRow(
                         column(width = 12,
                                DTOutput('dt_fenjian_ui')
                         )
                       )
              ),
              tabPanel("退换货",
                       fluidRow(
                         column(width = 6,
                                airDatepickerInput(
                                  inputId = "check_on_select2",
                                  value=c(floor_date(as.POSIXct(today()-1), "month"),as.POSIXct(today()-1)),
                                  label = "检测日期:",
                                  range = TRUE,
                                  placeholder = NULL,
                                  multiple = 5, 
                                  clearButton = TRUE
                                )
                         ),
                         column(width = 6,
                                virtualSelectInput(
                                  inputId = "product_name_select2",
                                  label = "产品类型:",
                                  choices = c("产成品-电动牙刷","产成品-吹风机"),
                                  selected = "产成品-吹风机",
                                  showValueAsTags = TRUE,
                                  search = TRUE,
                                  multiple = TRUE
                                ),
                                #textOutput("test")
                         )
                       ),
                       fluidRow(
                         column(width = 12,
                                DTOutput('dt_fenjian_ui2')
                         )
                       )
              )
            )
          )
        ),
        tabItem(
          tabName = "item2",
          fluidRow(
            valueBoxOutput("vbox_weixiu_1",width = 4),
            valueBoxOutput("vbox_weixiu_2",width = 4),
            valueBoxOutput("vbox_weixiu_3",width = 4)
          ),
          fluidRow(
            valueBoxOutput("vbox_weixiu_4",width = 3),
            valueBoxOutput("vbox_weixiu_5",width = 3),
            valueBoxOutput("vbox_weixiu_6",width = 2),
            valueBoxOutput("vbox_weixiu_7",width = 2),
            valueBoxOutput("vbox_weixiu_8",width = 2),
          ),
          tags$hr(),
          fluidRow(
            tabBox(
              width = 12,
              title=NULL,
              tabPanel("寄修全工序",
                       fluidRow(
                         column(width = 6,
                                airDatepickerInput(
                                  inputId = "check_on_select_weixiu_4",
                                  value=c(floor_date(as.POSIXct(today()-1), "month"),as.POSIXct(today()-1)),
                                  label = "发货日期:",
                                  range = TRUE,
                                  placeholder = NULL,
                                  multiple = 5, 
                                  clearButton = TRUE
                                )
                         ),
                         # column(width = 6,
                         #        virtualSelectInput(
                         #          inputId = "product_name_select_weixiu_4",
                         #          label = "产品类型:",
                         #          choices = c("产成品-电动牙刷","产成品-吹风机"),
                         #          selected = "产成品-吹风机",
                         #          showValueAsTags = TRUE,
                         #          search = TRUE,
                         #          multiple = TRUE
                         #        )
                         # )
                         column(width = 3,
                                virtualSelectInput(
                                  inputId = "bar_metric_jixiu",
                                  label = "选择柱形图指标：",
                                  choices = c("业务量_寄修","单均时效","业务量_风机","人效_风机","人效_牙刷"),
                                  selected = "业务量_寄修",
                                  showValueAsTags = TRUE,
                                  search = TRUE,
                                  multiple = FALSE
                                )
                         ),
                         column(width = 3,
                                virtualSelectInput(
                                  inputId = "line_metric_jixiu",
                                  label = "选择折线图指标：",
                                  choices = c("时效达成率_寄修","人效达成率_风机","人效达成率_牙刷","时效达成率_维修","时效达成率_质检","时效达成率_发货"),
                                  selected = "时效达成率_寄修",
                                  showValueAsTags = TRUE,
                                  search = TRUE,
                                  multiple = TRUE
                                )
                         )
                       ),
                       fluidRow(
                         column(
                           width = 12,
                           echarts4rOutput("combo_chart_jixiu")
                         )
                       ),
                       fluidRow(
                         column(width = 12,
                                DTOutput('dt_weixiu_ui_4')
                         )
                       )
              ),
              tabPanel("维修",
                       fluidRow(
                         column(width = 6,
                                airDatepickerInput(
                                  inputId = "check_on_select_weixiu_1",
                                  value=c(floor_date(as.POSIXct(today()-1), "month"),as.POSIXct(today()-1)),
                                  label = "维修完成日期:",
                                  range = TRUE,
                                  placeholder = NULL,
                                  multiple = 5, 
                                  clearButton = TRUE
                                )
                         ),
                         column(width = 3,
                                virtualSelectInput(
                                  inputId = "product_name_select_weixiu_1",
                                  label = "产品类型:",
                                  choices = c("产成品-电动牙刷","产成品-吹风机"),
                                  selected = "产成品-吹风机",
                                  showValueAsTags = TRUE,
                                  search = TRUE,
                                  multiple = FALSE
                                )
                         ),
                         column(width = 3,
                                virtualSelectInput(
                                  inputId = "per_name_select_weixiu_1",
                                  label = "服务人员:",
                                  choices = unique(dt_weixiu$per_name_weixiu),
                                  selected = unique(dt_weixiu$per_name_weixiu),
                                  #hideClearButton = FALSE,
                                  #showSelectedOptionsFirst = TRUE,
                                  noOfDisplayValues = 2,
                                  showValueAsTags = TRUE,
                                  search = TRUE,
                                  multiple = TRUE,
                                  updateOn = "close"
                                )
                         )
                       ),
                       fluidRow(
                         column(width = 12,
                                DTOutput('dt_weixiu_ui_1')
                         )
                       )
              ),
              tabPanel("质检",
                       fluidRow(
                         column(width = 6,
                                airDatepickerInput(
                                  inputId = "check_on_select_weixiu_2",
                                  value=c(floor_date(as.POSIXct(today()-1), "month"),as.POSIXct(today()-1)),
                                  label = "质检完成日期:",
                                  range = TRUE,
                                  placeholder = NULL,
                                  multiple = 5, 
                                  clearButton = TRUE
                                )
                         ),
                         column(width = 6,
                                virtualSelectInput(
                                  inputId = "product_name_select_weixiu_2",
                                  label = "产品类型:",
                                  choices = c("产成品-电动牙刷","产成品-吹风机"),
                                  selected = "产成品-吹风机",
                                  showValueAsTags = TRUE,
                                  search = TRUE,
                                  multiple = TRUE
                                ),
                                #textOutput("test")
                         )
                       ),
                       fluidRow(
                         column(width = 12,
                                DTOutput('dt_weixiu_ui_2')
                         )
                       )
              ),
              tabPanel("发货",
                       fluidRow(
                         column(width = 6,
                                airDatepickerInput(
                                  inputId = "check_on_select_weixiu_3",
                                  value=c(floor_date(as.POSIXct(today()-1), "month"),as.POSIXct(today()-1)),
                                  label = "发货日期:",
                                  range = TRUE,
                                  placeholder = NULL,
                                  multiple = 5, 
                                  clearButton = TRUE
                                )
                         ),
                         column(width = 6,
                                virtualSelectInput(
                                  inputId = "product_name_select_weixiu_3",
                                  label = "产品类型:",
                                  choices = c("产成品-电动牙刷","产成品-吹风机"),
                                  selected = "产成品-吹风机",
                                  showValueAsTags = TRUE,
                                  search = TRUE,
                                  multiple = TRUE
                                )
                                #textOutput("test")
                         )
                       ),
                       fluidRow(
                         column(width = 12,
                                DTOutput('dt_weixiu_ui_3')
                         )
                       )
              )
            )
          )
        )
      )
      
    }
    else {
      loginpage
    }
  })

    
#########################################################
  output$vbox <- renderValueBox(box_out(dt_fenjian_gbd,"dy","业务量",dt_fenjian_gbd_all$总业务量[2],percent_string("环比",dt_fenjian_gbd_all$总业务量[3],3),"-","coins","#F77251",if_else(dt_fenjian_gbd_all$总业务量[3]>0,"&uarr;","&darr;")))
  output$vbox2 <- renderValueBox(box_out(dt_fenjian_gbd,"dy","日均业务量",dt_fenjian_gbd_all$日均业务量[2],percent_string("环比",dt_fenjian_gbd_all$日均业务量[3],3),"-","coins","#F77251",if_else(dt_fenjian_gbd_all$日均业务量[3]>0,"&uarr;","&darr;")))
  output$vbox3 <- renderValueBox(box_out(dt_fenjian_gbd,"dy","人效",dt_fenjian_gbd_all$分拣组人效[2],percent_string("环比",dt_fenjian_gbd_all$分拣组人效[3],3),str_c("目标: ",KPI$分拣组人效[1]),"coins","#4BC8B6",if_else(dt_fenjian_gbd_all$分拣组人效[3]>0,"&uarr;","&darr;")))
  output$vbox4 <- renderValueBox(box_out(dt_fenjian_gbd,"dy","人效达成率",percent_string("",dt_fenjian_gbd_all$人效达成率[2],3),percent_string("环比",dt_fenjian_gbd_all$人效达成率[2]-dt_fenjian_gbd_all$人效达成率[1],3),"-","coins","#4BC8B6",if_else(dt_fenjian_gbd_all$人效达成率[3]>0,"&uarr;","&darr;")))
  output$vbox5 <- renderValueBox(box_out(dt_fenjian_gbd,"dy","单均时效",dt_fenjian_gbd_all$单均时效[2],percent_string("环比",dt_fenjian_gbd_all$单均时效[3],3),"-","coins","#03BFEF",if_else(dt_fenjian_gbd_all$单均时效[3]>0,"&uarr;","&darr;")))
  output$vbox6 <- renderValueBox(box_out(dt_fenjian_gbd,"dy","时效达成率",percent_string("",dt_fenjian_gbd_all$时效达成率[2],3),percent_string("环比",dt_fenjian_gbd_all$时效达成率[2]-dt_fenjian_gbd_all$时效达成率[1],3),percent_string("目标",KPI$分拣组时效达成率[1],2),"coins","#03BFEF",if_else(dt_fenjian_gbd_all$时效达成率[3]>0,"&uarr;","&darr;")))
  output$vbox_weixiu_1 <- renderValueBox(box_out(dt_jixiu_gbd,"dy","业务量_寄修",dt_jixiu_gbd_all$总业务量[2],percent_string("环比",dt_jixiu_gbd_all$总业务量[3],3),"-","coins","#F77251",if_else(dt_jixiu_gbd_all$总业务量[3]>0,"&uarr;","&darr;")))
  output$vbox_weixiu_2 <- renderValueBox(box_out(dt_jixiu_gbd,"dy","日均业务量",round(dt_jixiu_gbd_all$日均业务量[2],1),percent_string("环比",dt_jixiu_gbd_all$日均业务量[3],3),"-","coins","#F77251",if_else(dt_jixiu_gbd_all$日均业务量[3]>0,"&uarr;","&darr;")))
  output$vbox_weixiu_3 <- renderValueBox(box_out(dt_jixiu_gbd,"dy","时效达成率_寄修",percent_string("",dt_jixiu_gbd_all$时效达成率[2],3),percent_string("环比",dt_jixiu_gbd_all$时效达成率[2]-dt_jixiu_gbd_all$时效达成率[1],3),percent_string("目标",KPI$寄修组时效达成率[1],2),"coins","#03BFEF",if_else(dt_jixiu_gbd_all$时效达成率[3]>0,"&uarr;","&darr;")))
  output$vbox_weixiu_4 <- renderValueBox(box_out(dt_jixiu_gbd,"dy","人效达成率_风机",percent_string("",dt_jixiu_gbd_all$风机人效达成率[2],3),percent_string("环比",dt_jixiu_gbd_all$风机人效达成率[2]-dt_jixiu_gbd_all$风机人效达成率[1],3),"-","coins","#4BC8B6",if_else(dt_jixiu_gbd_all$风机人效达成率[3]>0,"&uarr;","&darr;")))
  output$vbox_weixiu_5 <- renderValueBox(box_out(dt_jixiu_gbd,"dy","人效达成率_牙刷",percent_string("",dt_jixiu_gbd_all$牙刷人效达成率[2],3),percent_string("环比",dt_jixiu_gbd_all$牙刷人效达成率[2]-dt_jixiu_gbd_all$牙刷人效达成率[1],3),"-","coins","#4BC8B6",if_else(dt_jixiu_gbd_all$牙刷人效达成率[3]>0,"&uarr;","&darr;")))
  output$vbox_weixiu_6 <- renderValueBox(box_out(dt_jixiu_gbd,"dy","时效达成率_维修",percent_string("",dt_jixiu_gbd_all$维修时效达成率[2],3),percent_string("环比",dt_jixiu_gbd_all$维修时效达成率[2]-dt_jixiu_gbd_all$维修时效达成率[1],3),percent_string("目标",KPI$维修时效达成率[1],2),"coins","#03BFEF",if_else(dt_jixiu_gbd_all$维修时效达成率[3]>0,"&uarr;","&darr;")))
  output$vbox_weixiu_7 <- renderValueBox(box_out(dt_jixiu_gbd,"dy","时效达成率_质检",percent_string("",dt_jixiu_gbd_all$质检时效达成率[2],3),percent_string("环比",dt_jixiu_gbd_all$质检时效达成率[2]-dt_jixiu_gbd_all$质检时效达成率[1],3),percent_string("目标",KPI$质检时效达成率[1],2),"coins","#03BFEF",if_else(dt_jixiu_gbd_all$质检时效达成率[3]>0,"&uarr;","&darr;")))
  output$vbox_weixiu_8 <- renderValueBox(box_out(dt_jixiu_gbd,"dy","时效达成率_发货",percent_string("",dt_jixiu_gbd_all$发货时效达成率[2],3),percent_string("环比",dt_jixiu_gbd_all$发货时效达成率[2]-dt_jixiu_gbd_all$发货时效达成率[1],3),percent_string("目标",KPI$发货时效达成率[1],2),"coins","#03BFEF",if_else(dt_jixiu_gbd_all$发货时效达成率[3]>0,"&uarr;","&darr;")))
  dt_fenjian_gbdp_filter <- reactive({
    dt_fenjian %>% 
      filter(productmodel_name %in% input$product_name_select3 ,between(new_checkon,input$check_on_select3[1],input$check_on_select3[2]+days(1))) %>% 
      gbd_fun("new_checkon","per_name_fenjian",KPI,"分拣组人效","分拣时长_小时")
  })
  dt_jixiu_gbd_filter <- reactive({
    gbd_fun(dt_jixiu,"new_deliveriedon","",KPI,"寄修组人效","寄修时长_小时") %>% 
      filter(between(ds,input$check_on_select_weixiu_4[1],input$check_on_select_weixiu_4[2])) %>% 
      select(-人数,-人效,-人效达成率) %>% 
      left_join(select(filter(dt_weixiu_gbdp,productmodel_name=="产成品-吹风机"),ds,业务量,人数,人效,人效达成率,业务量_不含流水线),by=c("ds"="ds"),suffix=c("_寄修","")) %>% 
      left_join(select(filter(dt_weixiu_gbdp,productmodel_name=="产成品-电动牙刷"),ds,业务量,人数,人效,人效达成率,业务量_不含流水线),by=c("ds"="ds"),suffix=c("_风机","_牙刷")) %>% 
      left_join(select(dt_weixiu_gbd,ds,时效达成单数,时效单数,时效达成率),by=c("ds"="ds"),suffix=c("_寄修","")) %>% 
      left_join(select(dt_zhijian_gbd,ds,时效达成单数,时效单数,时效达成率),by=c("ds"="ds"),suffix=c("_维修","")) %>%
      left_join(select(dt_fahuo_gbd,ds,时效达成单数,时效单数,时效达成率),by=c("ds"="ds"),suffix=c("_质检","_发货"))
  })
  dt_weixiu_gbd_filter <- reactive({
    dt_weixiu %>% 
    filter(productmodel_name %in% input$product_name_select_weixiu_1,
           between(ds,input$check_on_select_weixiu_1[1],input$check_on_select_weixiu_1[2]),
           per_name_weixiu %in% input$per_name_select_weixiu_1) %>% 
    group_by(ds,per_name_weixiu) %>% 
    mutate(per_n=n()) %>% 
    ungroup() %>% 
    group_by(ds,productmodel_name) %>% 
    summarise(业务量=n(),
              业务量_不含流水线=sum(if_else(per_n<KPI[1,"人效剔除_上限"]&per_n>KPI[1,"人效剔除_下限"],1,0)),
              人数=n_distinct(if_else(per_n<KPI[1,"人效剔除_上限"]&per_n>KPI[1,"人效剔除_下限"],per_name_weixiu,NA),na.rm = TRUE),
              人效=业务量_不含流水线/人数,
              时效=sum(维修时长_小时,na.rm = TRUE),
              单均时效=时效/业务量,
              时效达成单数=sum(if_else(时效类型=="完成",1,0),na.rm = TRUE),
              时效单数=sum(if_else(时效类型%in%c("完成","未完成"),1,0),na.rm = TRUE),
              时效达成率=时效达成单数/时效单数,
              .groups = "drop") %>% 
    mutate(mon=year(ds)*100+month(ds),
           dy=day(ds),
           人效达成率=人效/if_else(productmodel_name=="产成品-吹风机",KPI$寄修组吹风机人效[1],KPI$寄修组电动牙刷人效[1])) %>% 
    select(-productmodel_name)
  })
  dt_weixiu_gbd_filter_per <- reactive({
    a <- dt_weixiu %>% 
      filter(productmodel_name %in% input$product_name_select_weixiu_1,
             between(ds,input$check_on_select_weixiu_1[1],input$check_on_select_weixiu_1[2])) %>% 
      group_by(ds,per_name_weixiu) %>% 
      mutate(per_n=n()) %>% 
      ungroup() %>% 
    unique(a$per_name_weixiu)
  })
  
#####################################################
  output$dt_fenjian_ui <- renderDT({
    dt_fenjian_gbdp_filter <- dt_fenjian %>% 
      filter(applytype=="寄修/返修",productmodel_name %in% input$product_name_select ,between(new_checkon,input$check_on_select[1],input$check_on_select[2]+days(1))) %>% 
      gbd_fun("new_checkon","per_name_fenjian",KPI,"分拣组人效","分拣时长_小时") 
    # sketch <- sketch_fun(dt_fenjian_gbdp_filter)
    # dt_fenjian_gbdp_filter <- dt_fenjian_gbdp_filter %>% 
    #   select(-时效,-日均业务量,-时效单数,-业务量_不含流水线)
      
    dt_out(dt_fenjian_gbdp_filter,1,summa_sum_fenjian,summa_mean_fenjian,c(-3,-7,-10,-12,-13,-14),c(4,6),c(5,8)) 
      
  })
  output$dt_fenjian_ui2 <- renderDT({
    dt_fenjian_gbdp_filter <- dt_fenjian %>% 
      filter(applytype %in% c("退货","换货"),productmodel_name %in% input$product_name_select2 ,between(new_checkon,input$check_on_select2[1],input$check_on_select2[2]+days(1))) %>% 
      gbd_fun("new_checkon","per_name_fenjian",KPI,"分拣组人效","分拣时长_小时") 
    # sketch <- sketch_fun(dt_fenjian_gbdp_filter)
    # dt_fenjian_gbdp_filter <- dt_fenjian_gbdp_filter %>% 
    #   select(-时效,-日均业务量,-时效单数,-业务量_不含流水线)
    dt_out(dt_fenjian_gbdp_filter,1,summa_sum_fenjian,summa_mean_fenjian,c(-3,-7,-10,-12,-13,-14),c(4,6),c(5,8))
  })
  output$dt_fenjian_ui3 <- renderDT({
    dt_out(dt_fenjian_gbdp_filter(),1,summa_sum_fenjian,summa_mean_fenjian,c(-3,-7,-10,-12,-13,-14),c(4,6),c(5,8)) %>% 
      formatStyle(columns = 5,
                  background = styleColorBar(c(0,1,dt_fenjian_gbdp_filter()["人效达成率"]), '#fbb8a8'),
                  backgroundSize = '98% 80%',
                  backgroundRepeat = 'no-repeat',
                  backgroundPosition = 'center') %>% 
      formatStyle(columns = 8,
                  background = styleColorBar(c(0,1,dt_fenjian_gbdp_filter()["时效达成率"]), '#fbb8a8'),
                  backgroundSize = '98% 80%',
                  backgroundRepeat = 'no-repeat',
                  backgroundPosition = 'center')
  })
  #output$test <- renderPrint(input$check_on_select2[1])
  output$dt_weixiu_ui_4 <- renderDT({
    dt_out(dt_jixiu_gbd_filter(),1,summa_sum_jixiu,summa_mean_jixiu,c(-3,-6,-8,-9,-10,-12,-15,-17,-20,-22,-25,-28),c(3,7,10),c(5,8,11,13,15,17)) %>% 
      formatStyle(columns = "时效达成率_寄修",
                  background = styleColorBar(c(0,1,dt_jixiu_gbd_filter()["时效达成率_寄修"]), '#fbb8a8'),
                  backgroundSize = '98% 80%',
                  backgroundRepeat = 'no-repeat',
                  backgroundPosition = 'center') %>% 
      formatStyle(columns = "人效达成率_风机",
                  background = styleColorBar(c(0,1,dt_jixiu_gbd_filter()["人效达成率_风机"]), '#b7e9e1'),
                  backgroundSize = '98% 80%',
                  backgroundRepeat = 'no-repeat',
                  backgroundPosition = 'center') %>% 
      formatStyle(columns = "人效达成率_牙刷",
                  background = styleColorBar(c(0,1,dt_jixiu_gbd_filter()["人效达成率_牙刷"]), '#b7e9e1'),
                  backgroundSize = '98% 80%',
                  backgroundRepeat = 'no-repeat',
                  backgroundPosition = 'center') %>% 
      formatStyle(columns = "时效达成率_维修",
                  background = styleColorBar(c(0,1,dt_jixiu_gbd_filter()["时效达成率_维修"]), '#9ae5f8'),
                  backgroundSize = '98% 80%',
                  backgroundRepeat = 'no-repeat',
                  backgroundPosition = 'center') %>% 
      formatStyle(columns = "时效达成率_质检",
                  background = styleColorBar(c(0,1,dt_jixiu_gbd_filter()["时效达成率_质检"]), '#9ae5f8'),
                  backgroundSize = '98% 80%',
                  backgroundRepeat = 'no-repeat',
                  backgroundPosition = 'center') %>% 
      formatStyle(columns = "时效达成率_发货",
                  background = styleColorBar(c(0,1,dt_jixiu_gbd_filter()["时效达成率_发货"]), '#9ae5f8'),
                  backgroundSize = '98% 80%',
                  backgroundRepeat = 'no-repeat',
                  backgroundPosition = 'center')
  })
  # observeEvent(input$check_on_select_weixiu_1,{
  #   updateVirtualSelect(inputId = "per_name_select_weixiu_1", choices = dt_weixiu_gbd_filter_per())
  # })
  output$dt_weixiu_ui_1 <- renderDT({
    if(input$product_name_select_weixiu_1=="产成品-吹风机"){
      dt_out(dt_weixiu_gbd_filter(),1,summa_sum_weixiu_fenji,summa_sum_weixiu_fenji,c(-3,-6,-9,-11,-12),c(4,5),c(7,8))
    }else{
      dt_out(dt_weixiu_gbd_filter(),1,summa_sum_weixiu_yashuai,summa_sum_weixiu_yashuai,c(-3,-6,-9,-11,-12),c(4,5),c(7,8))
    }
  })
  output$dt_weixiu_ui_2 <- renderDT({
    dt_zhijian_gbd_filter <- dt_zhijian %>% 
      filter(productmodel_name %in% input$product_name_select_weixiu_2 ,between(ds,input$check_on_select_weixiu_2[1],input$check_on_select_weixiu_2[2])) %>% 
      gbd_fun("laifen_qualityrecordtime","",KPI,"质检人效","质检时长_小时")
    dt_out(dt_zhijian_gbd_filter,1,summa_sum_zhijian,summa_mean_zhijian,c(-3,-4,-5,-6,-9,-11,-12,-13),c(3),c(5))  
  })
  output$dt_weixiu_ui_3 <- renderDT({
    dt_fahuo_gbd_filter <- dt_fahuo %>% 
      filter(productmodel_name %in% input$product_name_select_weixiu_3 ,between(ds,input$check_on_select_weixiu_3[1],input$check_on_select_weixiu_3[2])) %>% 
      gbd_fun("new_deliveriedon","",KPI,"发货人效","发货时长_小时")
    dt_out(dt_fahuo_gbd_filter,1,summa_sum_zhijian,summa_mean_zhijian,c(-3,-4,-5,-6,-9,-11,-12,-13),c(3),c(5))  
  })
  output$combo_chart_fenjian <- renderEcharts4r({
    # 获取用户选择的指标
    bar_metric <- input$bar_metric_fenjian
    line_metric <- input$line_metric_fenjian
    # 创建组合图
    e <- dt_fenjian_gbdp_filter() %>%
      mutate(ds=as.character(ds)) %>% 
#      select(c(-3,-7,-10,-12,-13,-14)) %>% 
      e_charts(ds) %>%
      e_bar_(bar_metric, name = bar_metric,color=if_else(str_detect(bar_metric,"业务量"),"#F77251",if_else(str_detect(bar_metric,"人效"),"#4BC8B6","#03BFEF"))) %>%
      e_tooltip(trigger = "axis") %>%
      e_title("指标走势") %>%
      e_legend(bottom = 0) %>%
      e_x_axis(name = "日期") %>%
      e_y_axis(name = bar_metric)
    for (i in line_metric) {
      e <- e %>% 
        e_line_(i,y_index = 1)
    }
    e %>% e_y_axis(name = line_metric, index = 1,formatter = e_axis_formatter("percent", digits = 0))
  })
  output$combo_chart_jixiu <- renderEcharts4r({
    # 获取用户选择的指标
    bar_metric <- input$bar_metric_jixiu
    line_metric <- input$line_metric_jixiu
    # 创建组合图
    e <- dt_jixiu_gbd_filter() %>%
      mutate(ds=as.character(ds)) %>% 
#      select(c(-3,-7,-10,-12,-13,-14)) %>% 
      e_charts(ds) %>%
      e_bar_(bar_metric, name = bar_metric,color=if_else(str_detect(bar_metric,"业务量"),"#F77251",if_else(str_detect(bar_metric,"人效"),"#4BC8B6","#03BFEF"))) %>%
      e_tooltip(trigger = "axis") %>%
      e_title("指标走势") %>%
      e_legend(bottom = 0) %>%
      e_x_axis(name = "日期") %>%
      e_y_axis(name = bar_metric)
    for (i in line_metric) {
      e <- e %>% 
        e_line_(i,y_index = 1)
    }
    e %>% e_y_axis(name = line_metric, index = 1,formatter = e_axis_formatter("percent", digits = 0))
  })
  observeEvent(input$sidebar_close, {
    if(input$sidebar_close){
      shinyjs::runjs("document.querySelector('.main-sidebar').style.display = 'block';")
      shinyjs::runjs("document.querySelector('.main-header').style.display = 'flex';")
    }else{
      shinyjs::runjs("document.querySelector('.main-sidebar').style.display = 'none';")
      shinyjs::runjs("document.querySelector('.main-header').style.display = 'none';")
    }
  })
}

# Run the application 
shinyApp(ui = ui, server = server,options=(list(host = "0.0.0.0",port = 1888,launch.browser = TRUE)))

