from django.db import models

from business_app.models import MedicalInstitution, SalesOrder
from django_extend.base import ModelWithLog
from django_extend.models import User
from master_data.models import LogisticsCompany, LogisticsMaterial


# Create your models here.
class Transfusion_Order(ModelWithLog):
    id=models.AutoField(primary_key=True)
    order_no=models.CharField(verbose_name="输注单运号",max_length=50) #P + 日期 + 4位流水号
    coi_no=models.CharField(verbose_name="COI编号",max_length=50,null=True,blank=True) #输注申请时写入
    task_id=models.CharField(verbose_name="任务号",max_length=50,null=True,blank=True)
    source_type_choice=(("临床入组","临床入组"),("商业化订单","商业化订单"),)
    source_type=models.CharField(verbose_name="来源类型",choices=source_type_choice,max_length=50)
    # 商业化订单
    sales_order=models.ForeignKey(verbose_name="商业化订单",to=SalesOrder,on_delete=models.CASCADE,db_column="sales_order_id",null=True,blank=True)
    # 医疗机构默认从订单带过来
    medical_institution = models.ForeignKey(verbose_name="医疗机构", to=MedicalInstitution,
                                            on_delete=models.CASCADE, db_column="medical_institution_id",null=True)
    medical_address=models.CharField(verbose_name="医疗机构地址",max_length=2000,null=True,blank=True)
    # 预计输注时间 计划输注日期
    expect_transfusion_time=models.DateTimeField(verbose_name="计划输注日期",null=True,blank=True)
    # 实际输注时间
    actual_transfusion_time=models.DateTimeField(verbose_name="实际输注时间",null=True,blank=True)
    approve_json=models.CharField(verbose_name="审批信息",max_length=1000,null=True,blank=True)
    # 1、计划 2、确认 3、取消 4、已预约物流 5、已到医院 6、已完成
    order_status_choice=(
        ("0","草稿"),
        ("1","待审核"),
        ("2","确认"),
        ("3","取消"),
        ("4","已预约物流"),
        ("5","已提货"),#追溯提货调用我们的接口设置
        ("6","运输中"),#追溯发运调用我们的接口设置, 激活物流第一行的状态为生效
        ("7","已到医院"),#医疗机构接收更新状态
        ("8","已开箱"),
        ("9","已完成"),
        ("10","关闭"),# 停用此状态
    )
    order_status=models.CharField(verbose_name="订单状态",choices=order_status_choice,max_length=50,null=True,blank=True)
    creater=models.ForeignKey(verbose_name="创建人",to=User,on_delete=models.CASCADE,db_column="creater_id",null=True,blank=True,related_name="transfusion_order_creater_id")
    create_time=models.DateTimeField(verbose_name="创建时间",auto_now_add=True,null=True,blank=True)
    note = models.CharField(verbose_name="备注", max_length=2000,null=True,blank=True)
    transfusion_dose=models.CharField(verbose_name="输注剂量",max_length=50,null=True,blank=True)
    actual_transfusion_dose=models.CharField(verbose_name="实际输注剂量",max_length=50,null=True,blank=True)
    whsOutBillNo = models.CharField(verbose_name="追溯出库单号", max_length=50,null=True,blank=True)
    whsOutBillDate = models.DateTimeField(verbose_name="追溯出库日期",null=True,blank=True)
    unpacking_date = models.DateTimeField(verbose_name="开箱时间",null=True,blank=True)
    is_closed=models.BooleanField(verbose_name="是否关闭",default=False)
    is_deleted=models.BooleanField(verbose_name="是否删除",default=False)
    def __str__(self):
        return self.order_no
    class Meta:
        verbose_name = '输注订单'
        verbose_name_plural = '输注订单'
        ordering =["id"]
        db_table = "Transfusion_Order"
        

        permissions = (
            ("close_Transfusion_Order", "关闭输注订单"),
            ("re_actavite_Transfusion_Order", "反审输注订单"),
            ("dtp_receive_Transfusion_Order","DTP药房接收"),
            ("dtp_send_Transfusion_Order","DTP药房发出"),
            ("dtp_reject_Transfusion_Order","DTP药房拒收"),
            ("hospital_receive_Transfusion_Order","医院接收"),
            ("hospital_reject_Transfusion_Order","医院拒收"),
            ("open_box_confirm_Transfusion_Order","开箱确认"),
            ("resuscitation_and_transfusion_Transfusion_Order","复苏及输注"),
            ("hospital_return_Transfusion_Order","医院退货"),
            ("dtp_return_Transfusion_Order","DTP药房退货"),
            ("dtp_return_receive_Transfusion_Order","DTP退货接收"),
            )
                       

class Transfusion_Order_Detail(ModelWithLog):
    id=models.AutoField(primary_key=True)
    transfusion_order=models.ForeignKey(verbose_name="输注订单",to=Transfusion_Order,on_delete=models.CASCADE,db_column="transfusion_order_id")
    # 产品编码 MBatchNo Code
    product_code=models.CharField(verbose_name="产品编码",max_length=50,null=True,blank=True)
    # 产品名称 
    product_name=models.CharField(verbose_name="产品名称",max_length=500,null=True,blank=True)
    # 产品规格 
    product_spec=models.CharField(verbose_name="产品规格",max_length=500,null=True,blank=True)
    # 产品批号
    product_batch_no=models.CharField(verbose_name="产品批号",max_length=500,null=True,blank=True)
    # 产品序列号
    product_sn=models.CharField(verbose_name="产品序列号",max_length=500,null=True,blank=True)
    # 产品二维码
    product_qrcode=models.CharField(verbose_name="产品二维码",max_length=500,null=True,blank=True)
    # 细胞数
    cell_count=models.CharField(verbose_name="细胞数",max_length=50,null=True,blank=True)
    # 细胞数单位
    cell_count_unit=models.CharField(verbose_name="细胞数单位",max_length=50,null=True,blank=True)
    def __str__(self):
        return f"{self.transfusion_order.order_no}-{self.product_qrcode}"
    class Meta:
        db_table = "Transfusion_Order_Detail"
        verbose_name = '输注订单明细'
        verbose_name_plural = '输注订单明细'
        ordering =["id"]

class TransfusionOrderAttachment(ModelWithLog):
    file_id = models.CharField(verbose_name="文件ID", primary_key=True, max_length=50)
    name = models.CharField(verbose_name="文件名", max_length=500)
    ext = models.CharField(verbose_name="文件后缀", max_length=50)
    size = models.IntegerField(verbose_name="文件大小")
    root_dir = models.CharField(verbose_name="文件根目录", max_length=500,null=True,blank=True)
    file_path = models.CharField(verbose_name="文件路径", max_length=2000)
    form_type_choice = (
        ("输注申请", "输注申请"),
        ("复苏及输注", "复苏及输注"),
    )
    form_type = models.CharField(verbose_name="附件所对应的单据",choices=form_type_choice,max_length=50,null=True,blank=True)
    file_label_name = models.CharField(verbose_name="订单附件类型名称",max_length=50)
    transfusion_order = models.ForeignKey(verbose_name="订单", to=Transfusion_Order,on_delete=models.CASCADE, db_column="transfusion_order_id")
    last_update = models.DateTimeField(verbose_name="最后更新时间", auto_now=True)
    creater = models.ForeignKey(verbose_name="创建人", to=User,on_delete=models.CASCADE, db_column="creater_id",related_name="transfusion_order_attachment_creater_id",null=True)
    def __str__(self):
        return f"{self.transfusion_order.order_no}-{self.name}"
    class Meta:
        verbose_name = '输注订单附件信息'
        verbose_name_plural = '输注订单附件信息'
        ordering =["file_id"]
        db_table = "TransfusionOrderAttachment"

class Transfusion_Logistics(ModelWithLog):
    id = models.AutoField(primary_key=True)
    task_id = models.CharField(verbose_name="任务号", max_length=50,null=True,blank=True)
    transfusion_order = models.OneToOneField(verbose_name="输注订单", to=Transfusion_Order,
                                        on_delete=models.CASCADE, db_column="transfusion_order_id")
    # 物流单号
    logistics_no = models.CharField(verbose_name="三方物流单号", max_length=50)
    # 物流状态
    # TODO: 产品发运设置已发货？
    # TODO: 医疗机构接收已到达？
    logistics_status_choice = (
        ("已预约", "已预约"),
        ("已发货", "已发货"),
        ("已到达", "已到达"),
    )
    logistics_company = models.ForeignKey(verbose_name="物流公司", to=LogisticsCompany,on_delete=models.CASCADE, db_column="logistics_company_id",null=True,blank=True)
    logistics_status = models.CharField(verbose_name="物流状态", choices=logistics_status_choice, max_length=50)
    # 物流备注
    logistics_remark = models.CharField(verbose_name="物流备注", max_length=2000,null=True,blank=True)
    # 物流创建人
    creater = models.ForeignKey(verbose_name="创建人", to=User,on_delete=models.CASCADE, db_column="creater_id",related_name="tansfusion_logistics_creater_id",null=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    # 0-草稿 可以通过确认按钮编辑所有信息
    # 1-审核中 不可以通过确认、保存按钮编辑所有信息
    # 2-已审核  不可以通过确认、保存按钮编辑所有信息
    status_choice = (
        ("0", "草稿"),
        ("1", "审核中"),
        ("2", "已审核"),
    )
    status=models.CharField(verbose_name="状态",max_length=50,null=True,blank=True,choices=status_choice)
    is_closed=models.BooleanField(verbose_name="是否关闭",default=False)
    def __str__(self):
        return f"{self.transfusion_order.order_no}-{self.logistics_no}"
    class Meta:
        verbose_name = '输注物流信息'
        verbose_name_plural = '输注物流信息'
        ordering =["id"]
        db_table = "Transfusion_Logistics"
        # 反审核,审核
        permissions = (
            ("approve_Transfusion_Logistics", "审核"),
            ("re_actavite_Transfusion_Logistics", "反审核"),
            )
            


class Transfusion_Logistics_Detail(ModelWithLog):
    id = models.AutoField(primary_key=True)
    transfusion_logistics = models.ForeignKey(verbose_name="输注物流信息", to=Transfusion_Logistics,
                                        on_delete=models.CASCADE, db_column="transfusion_logistics_id",null=True)
    logistics_no = models.CharField(verbose_name="三方物流单号", max_length=50)
    # 科济仓库、DTP药房、医疗机构
    from_address_type=models.CharField(verbose_name="出发地类型",max_length=50,null=True,blank=True)
    # 科济仓库、DTP药房、医疗机构的ID
    from_address_id=models.IntegerField(verbose_name="出发地ID",null=True,blank=True)
    from_contact_user = models.IntegerField(verbose_name="出发地物流人员",null=True,blank=True)
    from_contact = models.CharField(verbose_name="出发地联系人", max_length=50,null=True,blank=True)
    from_tel = models.CharField(verbose_name="出发地联系电话", max_length=50,null=True,blank=True)
    from_address = models.CharField(verbose_name="出发地地址", max_length=2000,null=True,blank=True)
    from_address_time = models.DateTimeField(verbose_name="发出时间",null=True,blank=True)
    # from_address_operater=models.ForeignKey(verbose_name="出发地操作人", to=User,on_delete=models.CASCADE,db_column="from_address_operater_id",related_name="from_address_operater_id",null=True)
    from_address_remark = models.CharField(verbose_name="出发地备注", max_length=2000,null=True,blank=True)
    # 科济仓库、DTP药房、医疗机构
    to_address_type=models.CharField(verbose_name="目的地类型",max_length=50,null=True,blank=True)
    # 科济仓库、DTP药房、医疗机构的ID
    to_address_id=models.IntegerField(verbose_name="目的地ID",null=True,blank=True)
    to_contact = models.CharField(verbose_name="目的地联系人", max_length=50,null=True,blank=True)
    to_contact_user = models.IntegerField(verbose_name="目的地物流人员",null=True,blank=True)
    to_tel = models.CharField(verbose_name="目的地联系电话", max_length=50,null=True,blank=True)
    to_address = models.CharField(verbose_name="目的地地址", max_length=2000,null=True,blank=True)
    to_address_time = models.DateTimeField(verbose_name="接收时间",null=True,blank=True)
    # to_address_operater=models.ForeignKey(verbose_name="目的地操作人", to=User,on_delete=models.CASCADE,db_column="to_address_operater_id",related_name="to_address_operater_id",null=True)
    to_address_remark = models.CharField(verbose_name="目的地备注", max_length=2000,null=True,blank=True)
    order_index = models.IntegerField(verbose_name="行号",null=True,blank=True)
    # 状态
    # 0-未生效 单据创建默认状态-未审核, 直接修改单据中物流人员信息。不显示变更、更换按钮
    # 1-已生效 物料审核后，可以提货单确认。 未出发前，可以变更物流人员信息。
    # 2-产品提货后 可以做产品发运，不可以变更物流人员信息。
    # 3-产品发运后 出发地物流人员不能改，这时可以更换物料资料(保留旧行，新增新行) 
    # 4-医院接收   这时不显示变更、更换按钮。
    # 0 成品物流单据创建初始状态
    # 1 单据审核通过设置为1，科济仓库提货过滤为1的行
    # 2 提货后设置为2，科济仓库发运过滤为2的行
    # 3 发运后设置为3
    # DTP OR 医疗机构接收读取过滤为3的行，接收后设置为4
    # DTP 接收更新下一行状态设置为1，DTP发货更新为3，DTP没有物流提货
    # 医疗机构接收 同样过滤为3的行 and to_address_type=医疗机构
    status_choice = (
        ("0", "未生效"),
        ("1", "已生效"),
        ("2", "物流提货"),
        ("3", "产品发运"),
        ("4", "已到达"),
    )
    status = models.CharField(verbose_name="状态", choices=status_choice, max_length=50)
    # 正向物流，反向物流
    logistics_type_choice = (
        (1, "正向物流"),
        (2, "反向物流"),
    )
    logistics_type = models.IntegerField(verbose_name="物流类型", choices=logistics_type_choice,default=1)
    
    # 物流备注
    logistics_remark = models.CharField(verbose_name="物流备注", max_length=2000,null=True,blank=True)
    def __str__(self):
        return f"{self.transfusion_logistics.transfusion_order.order_no}-{self.logistics_type_choice[int(self.logistics_type)-1][1]} 出发地:{self.from_address_type}-"
    class Meta:
        verbose_name = '输注物流明细信息'
        verbose_name_plural = '输注物流明细信息'
        ordering =["id"]
        db_table = "Transfusion_Logistics_Detail"
        

class Transfusion_Logistics_Attachment(ModelWithLog):
    file_id = models.CharField(verbose_name="文件ID", primary_key=True, max_length=50)
    name = models.CharField(verbose_name="文件名", max_length=500)
    ext = models.CharField(verbose_name="文件后缀", max_length=50)
    size = models.IntegerField(verbose_name="文件大小")
    root_dir = models.CharField(verbose_name="文件根目录", max_length=500,null=True,blank=True)
    file_path = models.CharField(verbose_name="文件路径", max_length=2000)
    form_type_choice = (
        ("DTP药房接收", "DTP药房接收"),
        ("DTP药房发放", "DTP药房发放"),
        ("DTP药房退货", "DTP药房退货"),
        ("医疗机构接收", "医疗机构接收"),
        ("医疗机构退货", "医疗机构退货"),
    )
    form_type = models.CharField(verbose_name="附件所对应的单据", choices=form_type_choice, max_length=50)
    file_label_name = models.CharField(verbose_name="订单附件类型名称", max_length=50)
    transfusion_logistics = models.ForeignKey(verbose_name="成品物流", to=Transfusion_Logistics,on_delete=models.CASCADE, db_column="transfusion_logistics_id")
    last_update = models.DateTimeField(verbose_name="最后更新时间", auto_now=True)
    creater = models.ForeignKey(verbose_name="创建人", to=User,on_delete=models.CASCADE, db_column="creater_id",related_name="transfusion_logistics_attachment_creater_id",null=True)
    def __str__(self):
        return f"{self.transfusion_logistics.transfusion_order.order_no}-{self.name}"
    class Meta:
        verbose_name = '成品物流附件信息'
        verbose_name_plural = '成品物流附件信息'
        ordering =["file_id"]
        db_table = "Transfusion_Logistics_Attachment"
        
class Transfusion_Logistics_Material(ModelWithLog):
    id = models.AutoField(primary_key=True)
    transfusion_logistics = models.ForeignKey(verbose_name="输注物流信息", to=Transfusion_Logistics,
                                        on_delete=models.CASCADE, db_column="transfusion_logistics_id")
    material_type_choice = (
        ("温度计", "温度计"),
        ("保温箱", "保温箱"),
        ("液氮罐", "液氮罐"),
    )
    material_type = models.CharField(verbose_name="物流资料类型", choices=material_type_choice, max_length=50)
    logistics_material = models.ForeignKey(verbose_name="物流资料ID", to=LogisticsMaterial,
                                        on_delete=models.CASCADE, db_column="logistics_material_id",null=True)
    material_model = models.CharField(verbose_name="规格型号", max_length=500)
    material_sn = models.CharField(verbose_name="物料序列号", max_length=500)
    material_remark = models.CharField(verbose_name="物料备注", max_length=2000,null=True,blank=True)
    # 0-已被替换 1-生效
    status=models.BooleanField(verbose_name="状态")
    from_line_id=models.ForeignKey(verbose_name="来源行ID", to="self",on_delete=models.CASCADE,db_column="from_line_id",null=True,blank=True)
    order_index = models.IntegerField(verbose_name="行号",null=True,blank=True)
    def __str__(self):
        return f"{self.transfusion_logistics.transfusion_order.order_no}-{self.material_sn}"
    class Meta:
        verbose_name = '输注物流资料信息'
        verbose_name_plural = '输注物流资料信息'
        ordering =["id"]
        db_table = "Transfusion_Logistics_Material"