from c_mssql.mssql_source import Mssql_Source,Mssql_Conn
import json,decimal
import datetime

from c_mssql import DB_Config
dbc_trace_business=DB_Config(server="192.168.105.11",port=1433,database="TSC-P",user="traceservice",password="WRefe34!we",driver="ODBC Driver 17 for SQL Server")
# [trace_business]
# NAME= TSC-P
# HOST= 192.168.105.11
# PORT= 1433
# USER= traceservice
# PASSWORD= WRefe34!we
# driver=ODBC Driver 17 for SQL Server

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S') if type(obj)==datetime.datetime else None
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().strftime('%H:%M:%S')
        #  Object of type Decimal is not JSON serializable
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)
        
trace_conn=Mssql_Conn(dbc_trace_business)

trace_source=Mssql_Source(dbc_trace_business)

sql_str="""select PlanDeliverBillInteralNo,t1.WhsOutBillNo,PackEditDate as whsOutBillDate
into #T_Pack
from [TSC-P].DBO.WhsOutReqBill t1r
inner join [TSC-P].DBO.WhsOutBill t1 on t1r.WhsOutReqBillID=t1.WhsOutReqBillID
where 1=1
and t1r.WhsBillTypeCode='SaleReq'
and t1.WhsBillTypeCode='Sale'
and t1.[Status]='3';"""


trace_conn.open()
cursor=trace_conn.execute(sql_str)


cursor=trace_conn.execute("""select 
        v1.sales_order_id,
        so.order_no as sale_order_no,
        v1.order_no,
        v1.medical_institution_id as HostipalID,
        v1.create_time,
        v1.is_closed,
        v1.expect_transfusion_time,
        v1.actual_transfusion_time,
        (select 
            product_batch_no,
            product_sn,
            product_qrcode,
            cell_count,
            cell_count_unit
            from [TraceApp-P].[dbo].Transfusion_Order_Detail 
            where transfusion_order_id=v1.id
        for json path ) as details,
        (select l2.order_index,
        CASE WHEN l2.from_address_type='DTP药房' then from_dtp.dtp_name else l2.from_address_type end as from_address,
        l2.from_address_time,
        CASE WHEN l2.to_address_type='DTP药房' then to_dtp.dtp_name else l2.to_address_type end as to_address,
        l2.to_address_time
        from [TraceApp-P].[dbo].Transfusion_Logistics l1 with(nolock)
        inner join [TraceApp-P].[dbo].Transfusion_Logistics_Detail l2 with(nolock) on l1.id=l2.transfusion_logistics_id
        left join [TraceApp-P].[dbo].DTP from_dtp WITH(NOLOCK) on l2.from_address_id=from_dtp.id
        left join [TraceApp-P].[dbo].DTP to_dtp WITH(NOLOCK) on l2.to_address_id=to_dtp.id
        where 1=1
        and l1.transfusion_order_id=v1.id
        order by order_index for json path) as logistics_details
        from [TraceApp-P].[dbo].Transfusion_Order v1 with(nolock) 
        inner join [TraceApp-P].[dbo].SalesOrder so with(nolock) on v1.sales_order_id=so.id
        left join #T_Pack v2 on v1.order_no=v2.PlanDeliverBillInteralNo
        where 1=1""")


column_dict=trace_conn.column_dict()
# sale_order_no
transfusion_data_dict={}

row=cursor.fetchone()
while row:
    row_dict=dict(zip(column_dict,row))
    if row[1] not in transfusion_data_dict:
        transfusion_data_dict[row[1]]=[row_dict]
    else:
        transfusion_data_dict[row[1]].append(row_dict)
    row=cursor.fetchone()
trace_conn.execute("drop table #T_Pack")
trace_conn.close()


sql_str="""
select distinct
pbw.ProdBatchID,
ws.WarehouseStockID,
ws.COANoQ,ws.COANo,
ws.BatchNo as ProdBatchCode,
ws.ProdReleaseUserNameQ as 制药快速放行,
ws.ReleaseDateFactoryQ as 制药快速放行日期,
ws.ProdReleaseDateQ as 制药快速放行操作时间,
ws.ProdReleaseUserNameQ1 as MAH快速放行,
ws.ReleaseDateMAHQ as MAH快速放行日期,
ws.ProdReleaseDateQ1 as MAH快速放行操作时间,
(select UserName from [TSC-P]..Users where UserID=ws.ProdReleaseUserID1)  AS 制药常规放行,
ws.ReleaseDateFactory	AS 制药常规放行日期,
ws.ProdReleaseEditDate1 AS 制药常规放行操作时间,
(select UserName from [TSC-P]..Users where UserID=ws.ProdReleaseUserID2) AS MAH常规放行,
ws.ReleaseDateMAH AS MAH常规放行日期,
ws.ProdReleaseDate2	AS MAH常规放行操作时间,
IIF(ws.QualityDetailStatus='G2','常规放行',IIF(ws.QualityDetailStatus='G5','不予放行',IIF(ws.QualityDetailStatusQ='G1','快速放行','待检'))) as QualityStatus
from [TSC-P]..WhsInReqBill v1 with(nolock)
inner join [TSC-P]..ProdPlanOfWeek pbw on v1.ProdPlanOfWeekID=pbw.ProdPlanOfWeekID
inner join [TSC-P]..WhsInBill v2 on v1.WhsInReqBillID=v2.WhsInReqBillID 
inner join [TSC-P]..WhsInBillDetail v2d on v2.WhsInBillID=v2d.WhsInBillID 
inner join [TSC-P]..WarehouseStock ws on v2d.WarehouseStockID=ws.WarehouseStockID
where 1=1
and v2.[Status]='3'
and v1.[WhsBillTypeCode]='ProdInReq'
"""

trace_conn.open()
cursor=trace_conn.execute(sql_str)

column_dict=trace_conn.column_dict()
prod_batch_product_data_dict={}

row=cursor.fetchone()
while row:
    prod_batch_product_data_dict[row[0]]=dict(zip(column_dict,row))
    row=cursor.fetchone()


trace_conn.close()


sql_str="""select 
v1.SaleOrderNo,
v1.ProdBatchID,
V1.ProdBatchCode,
v1.CoiNo,
v1.BillNo,
v1.BatchNo,
V1.ProdDate,
v1.ExpDate,
v1.CardCount,
V1.ReceiveUserID,
V1.ReceiveDate,
v2.Operation as ReleaseOperation,
v2.OperationDate as ReleaseDate
from [BI_DW]..v_ProdIn_PBMC v1 
left join [BI_DW]..V_PbmcRelease V2 ON V1.BatchNo=V2.BatchNo

"""

trace_conn.open()
cursor=trace_conn.execute(sql_str)
column_dict=trace_conn.column_dict()
prod_batch_pbmc_data_dict={}

row=cursor.fetchone()
while row:
    prod_batch_pbmc_data_dict[row[1]]=dict(zip(column_dict,row))
    row=cursor.fetchone()

trace_conn.close()


sql_str="""select  
v1.ProdBatchCode,
v4.ProcName,
MIN(v3.WorkStartTime) OVER(PARTITION BY v1.ProdBatchID) AS WorkStartTime,v3.WorkEndTime,
ROW_NUMBER() OVER(PARTITION BY v1.ProdBatchID ORDER BY v3.ProdPlanDate ,v3.WorkEndTime DESC) AS row_id
FROM [TSC-P].[dbo].ProdBatch v1 with(nolock)
inner join [TSC-P].[dbo].ProdBatchDetail v2 with(nolock) on v1.ProdBatchID=v2.ProdBatchID
inner join [TSC-P].[dbo].ProdPlanOfWeek v3 with(nolock) on v1.ProdBatchID=v3.ProdBatchID and v2.ProdBatchDetailRNo=v3.ProdBatchDetailRNo
inner join [TSC-P].[dbo].Process v4 with(nolock) on v2.ProcessID=v4.ProcessID
inner join [TSC-P].[dbo].SaleOrder so with(nolock) on v1.SaleOrderID=so.SaleOrderID
inner join [TSC-P].[dbo].Workshop v5 with(nolock) on v1.WorkshopID=v5.WorkshopID
inner join [TSC-P].[dbo].TechniqueStandardEd v6 with(nolock) on V1.TechniqueStandardID=v6.TechniqueStandardID
WHERE 1=1
and v1.ProdBatchStatus in ('4','5','7')
and so.SCustomerNo>='000004'
"""


trace_conn.open()
cursor=trace_conn.execute(sql_str)
column_dict=trace_conn.column_dict()
prod_batch_detail_data_dict={}
row=cursor.fetchone()
while row:
    prod_batch_detail_data_dict[row[0]]=dict(zip(column_dict,row))
    row=cursor.fetchone()
trace_conn.close()



trace_conn.open()
cursor=trace_conn.execute("""SELECT [SaleOrderNo]
      ,[ProdBatchID]
      ,[ProdBatchCode]
      ,[CoiNo]
      ,[WorkshopName]
      ,[TechniqueStandardName]
      ,[ProdBatchStatus]
      ,[EndRemark]
      ,[AuditDate]
      ,[ProcName]
      ,[WorkStartTime]
      ,[WorkEndTime]
        FROM [BI_DW].[dbo].[DIM_ProdBatch]""")
column_dict=trace_conn.column_dict()
# CoiNo
prod_batch_data_dict={}
row=cursor.fetchone()
while row:
    row_dict=dict(zip(column_dict,row))
    row_dict["PBMC"]=prod_batch_pbmc_data_dict.get(row[1],{})
    row_dict["Product"]=prod_batch_product_data_dict.get(row[1],{})
    row_dict["Detail"]=prod_batch_detail_data_dict.get(row[2],{})
    if row[3] not in prod_batch_data_dict:
        prod_batch_data_dict[row[3]]=[row_dict]
    else:
        prod_batch_data_dict[row[3]].append(row_dict)

    row=cursor.fetchone()
trace_conn.close()

trace_conn.open()
cursor=trace_conn.execute("""SELECT 
       [SaleOrderNo]
      ,[DanCaiNo]
      ,[HostipalID]
      ,[plan_apheresis_date]
      ,[CoiNo]
      ,[apheresis_date]
      ,[apheresis_start]
      ,[apheresis_end]
      ,[order_status]
      ,[is_closed]
      ,[Apheresis_ArrivalDate]
      ,[Apheresis_ReleaseDate]
      ,[DanCaiVolume]
      ,[QualityDetailStatus]
      ,[BatchNo]
  FROM [BI_DW].[dbo].[FACT_Apheresis_Order]""")
column_dict=trace_conn.column_dict()
apheresis_order_data_dict={}
row=cursor.fetchone()
while row:
    row_dict=dict(zip(column_dict,row))
    row_dict["ProdBatch"]=prod_batch_data_dict.get(row[4],[])
    if row[0] not in apheresis_order_data_dict:
        apheresis_order_data_dict[row[0]]=[row_dict]
    else:
        apheresis_order_data_dict[row[0]].append(row_dict)
    row=cursor.fetchone()
trace_conn.close()

sql_str="""
SELECT [SaleOrderNo]
      ,[SaleOrderNoFix]
FROM [BI_DW].[dbo].[T_Correct_SaleOrderNo]
union ALL
SELECT [SaleOrderNo]=order_no
      ,[SaleOrderNoFix]=[order_no]
from [TraceApp-P].dbo.SalesOrder
order by SaleOrderNo
"""
trace_conn.open()
cursor=trace_conn.execute(sql_str)
row=cursor.fetchone()
sale_order_mapping_dict={}
while row:
    if row[0] not in sale_order_mapping_dict:
        sale_order_mapping_dict[row[0]]=[row[1]]
    else:
        sale_order_mapping_dict[row[0]].append(row[1])
    row=cursor.fetchone()
trace_conn.close()


sql_str="""SELECT [SaleOrderNo]
      ,[ConfirmDate]
  FROM [BI_DW].[dbo].[T_Correct_SaleOrderConfirm]"""
trace_conn.open()
cursor=trace_conn.execute(sql_str)
row=cursor.fetchone()
sale_order_confirm_date_dict={}
while row:
    sale_order_confirm_date_dict[row[0]]=row[1]
    row=cursor.fetchone()
trace_conn.close()


trace_conn.open()
cursor=trace_conn.execute("""select 
                            wft.finish_time as ApproveTime,
                            wft2.finish_time as NoticeProduceTime,
                            so.id as sale_order_id,
                            SaleOrderNo=so.order_no,
                            SaleOrderDate=so.order_date,
                            HostipalID=so.medical_institution_id,
                            SCustomerNo=so.patient_code,
                            SCustomerName=so.patient_name,
                            SCustomerNameSX=so.patient_name_abb,
                            SaleOrderType=IIF(so.order_type=2,'择期订单','常规订单')  ,
                            casT(IIF(so.order_status='关闭',1,0) as BIT) AS is_closed
                            from [TraceApp-P].[dbo].[SalesOrder] so with(nolock)
                            left join [BI_DW].[dbo].T_Correct_SaleOrderType sot with(nolock) on so.order_no=sot.SaleOrderNo
                            left join [TraceApp-P].[dbo].[BPM_WorkFlow_Task] wft with(nolock) on so.task_Id=wft.task_Id
                            left join [TraceApp-P].[dbo].[BPM_WorkFlow_Task] wft2 with(nolock) on so.delayed_task_id=wft2.task_Id
                            where 1=1
                            and so.order_status <>'草稿'
                            and so.order_no not in ('CLS-24-0014','CLS-24-0015','CLS-24-0016')
                            and so.is_deleted=0
                            and so.order_no not in (select SaleOrderNoFix from [BI_DW].[dbo].T_Correct_SaleOrderNo with(nolock))
                            """)

column_dict=trace_conn.column_dict()
row=cursor.fetchone()
data_list=[]
while row:
    sale_order_data_dict=dict(zip(column_dict,row))
    sale_order_data_dict["Apheresis"]=[]
    sale_order_data_dict["Transfusion"]=[]
    for sale_order_no in sale_order_mapping_dict[sale_order_data_dict["SaleOrderNo"]]:
        sale_order_data_dict["Apheresis"]+=apheresis_order_data_dict.get(sale_order_no,[])
        sale_order_data_dict["Transfusion"]+=transfusion_data_dict.get(sale_order_no,[])
    confirm_date=None
    if sale_order_data_dict["SaleOrderType"]=="常规订单":
        for apheresis_data_row in sale_order_data_dict["Apheresis"]:
            if apheresis_data_row["QualityDetailStatus"] in ('常规放行','限制性放行'):
                confirm_date=apheresis_data_row["Apheresis_ReleaseDate"]
                break
    elif sale_order_data_dict["SaleOrderType"]=="择期订单":
        if sale_order_data_dict["SaleOrderNo"] in sale_order_confirm_date_dict:
            confirm_date=sale_order_confirm_date_dict[sale_order_data_dict["SaleOrderNo"]]
        else:
            for apheresis_data_row in sale_order_data_dict["Apheresis"]:
                for prod_batch_data in apheresis_data_row.get("ProdBatch",[]):
                    pbmc_data=prod_batch_data.get("PBMC",{})
                    if pbmc_data.get("ReleaseOperation","") in ('XZFX','HG'):
                        confirm_date=pbmc_data["ReleaseDate"]
                        break
    sale_order_data_dict["ConfirmDate"]=confirm_date                    
    data_list.append(sale_order_data_dict)
    row=cursor.fetchone()
                                            
trace_conn.close()


# 将datalist转成json写入test2.json
with open("test2.json", "w",encoding="utf-8") as f:
    f.write(JSONEncoder().encode(data_list))