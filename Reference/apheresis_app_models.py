from django.db import models

from aps_app.models import ApsTask
from business_app.models import MedicalInstitution
from django_extend.base import ModelWithLog
from django_extend.models import User
from master_data.models import LogisticsCompany, LogisticsMaterial


# Create your models here.
class DonorInfo(ModelWithLog):
    id = models.AutoField(primary_key=True)
    # 临床受试者来源 临床入组。 商业化订单 来自商业化订单 。 健康人 来自健康采血单
    source_type_choice=(("临床入组","临床入组"),("商业化订单","商业化订单"),("健康人","健康人"),)
    source_type=models.CharField(verbose_name="来源类型",max_length=50)
    source_id = models.IntegerField(verbose_name="来源ID")
    # 供者编号 临床入组-等QA分配 商业化-订单的患者编号 健康人-等QA分配
    donor_code = models.CharField(verbose_name="供者编号", unique=True, max_length=50)
    donor_name = models.CharField(verbose_name="供者姓名", max_length=50,null=True,blank=True)
    # 供者姓名缩写
    donor_name_abb = models.CharField(verbose_name="供者姓名缩写", max_length=50)
    # 患者性别
    gender=models.CharField(verbose_name="性别", max_length=50,db_column="gender",null=True,blank=True)
    # 患者生日
    birthday=models.DateField(verbose_name="生日",db_column="birthday",null=True,blank=True)
    # 证件类型
    id_type_choice = (
        ("SFZ", "身份证"),
        ("HZ", "护照"),
        ("TXZ", "港澳居民来往内地通行证"),
        ("TW", "台湾居民来往大陆通行证"),
        ("WAIGUOREN", "外国人永久居留身份证"),
        ("HKMOJUMIN", "港澳台居民居住证"),
    )
    id_type = models.CharField(verbose_name="证件类型", choices=id_type_choice, max_length=50,null=True,blank=True)
    # 证件号码
    id_number = models.CharField(verbose_name="证件号码", max_length=50,null=True,blank=True)
    def __str__(self):
        return self.donor_code
    class Meta:
        verbose_name = '供者信息'
        verbose_name_plural = '供者信息'
        ordering =["id"]
        db_table = "DonorInfo"


class Apheresis_Order(ModelWithLog):
    id = models.AutoField(primary_key=True)
    order_no = models.CharField(verbose_name="采集单号", unique=True, max_length=50)
    coi_no=models.CharField(verbose_name="COI编号",max_length=50,null=True,blank=True)
    task_id = models.CharField(verbose_name="任务ID", max_length=50,null=True,blank=True)
    source_type_choice=(("临床入组","临床入组"),("商业化订单","商业化订单"),("健康人","健康人"),)
    source_type=models.CharField(verbose_name="来源类型",choices=source_type_choice,max_length=50)
    source_order_id = models.IntegerField(verbose_name="来源订单ID",null=True,blank=True)
    # 采集医疗机构
    medical_institution = models.ForeignKey(verbose_name="采集医疗", to=MedicalInstitution,
                                            on_delete=models.CASCADE, db_column="medical_institution_id",null=True,blank=True)
    medical_address = models.CharField(verbose_name="医疗机构地址", max_length=2000,null=True,blank=True)
    creater = models.ForeignKey(verbose_name="创建人", to=User,on_delete=models.CASCADE,db_column="creater_id",related_name="apheresis_order_creater_id",null=True,blank=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True,null=True,blank=True)
    # 计划单采日期
    plan_apheresis_date = models.DateTimeField(verbose_name="计划单采日期",null=True,blank=True) #增加时分秒 上午10:00 下午14:00
    # 实际单采日期 发运后，回写实际日期，发运表单手填 开始 结束
    actual_apheresis_date = models.DateField(verbose_name="实际单采日期",null=True,blank=True)
    # 1、单采确认预约 更新plan_cmc_date，根据plan_apheresis_date+运输。2、物流预约 更改新plan_cmc_date，根据logistics_plan_to_hospital+运输时间。3-单采发运 更新plan_cmc_date，根据apheresis_end+运输时间。
    # APS介入，改为手动填写 类型改为datetime 打包发运不在自动计算且不允许手动填写
    plan_cmc_date = models.DateTimeField(verbose_name="预计到达工厂日期",null=True,blank=True)
    apheresis_start = models.DateTimeField(verbose_name="单采开始时间",null=True,blank=True)
    apheresis_end = models.DateTimeField(verbose_name="单采结束时间",null=True,blank=True)
    # 1、计划 2、确认 3、取消 4、已预约物流 5、已到医院 6、已完成
    # 在本系统中单采接收时更新状态为已完成
    order_status_choice = (("计划", "计划"),("预占位","预占位"),("审核中","审核中"), ("确认", "确认"), ("关闭", "关闭"), ("已预约物流", "已预约物流"), ("已到医院", "已到医院"),("等待接收","等待接收"), ("已完成", "已完成"),)
    # 单据创建 ，只有 预占位，确认预约 
    # 单据(预占位，确认预约)提交后，提交事件中把状态变为审核中 。不可从表单页面修改单据信息。只能通过流程修改单据信息。
    # 预占位审核完成后，，提交事件中把状态变为预占位。(表单页面显示 确认预约 反审核(单据返回到计划状态，流程激活并回到开始节点) 按钮)
    # 确认预约审核完成后， MAH提交事件中把状态变为确认。(表单页面显示 反审核(单据返回到计划状态，流程激活并回到开始节点) 按钮)
    order_status = models.CharField(verbose_name="订单状态", choices=order_status_choice, max_length=50,null=True,blank=True)
    # 供者信息
    donor_id=models.ForeignKey(verbose_name="供者信息", to=DonorInfo,on_delete=models.CASCADE, db_column="donor_id",null=True,blank=True,related_name="donor_id")
    is_deleted=models.BooleanField(verbose_name="是否删除",default=False)
    is_closed=models.BooleanField(verbose_name="是否关闭",default=False)
    approve_json=models.CharField(verbose_name="审批信息",max_length=1000,null=True,blank=True)
    aps_task=models.ForeignKey(verbose_name="预约任务", to=ApsTask,on_delete=models.SET_NULL, db_column="aps_task_id",null=True,blank=True)
    def __str__(self):
        return self.order_no
    class Meta:
        verbose_name = '采集订单信息'
        verbose_name_plural = '采集订单信息'
        ordering =["id"]
        db_table = "Apheresis_Order"
        permissions = (("close_Apheresis_Order", "关闭采集订单"),("re_actavite_Apheresis_Order", "反审采集订单"),
                       ("confirm_Apheresis_Order", "单采提货单确认"),("start_Apheresis_Order", "单采打包发运"),
                    )
                       
                       

class Apheresis_Order_Detail(ModelWithLog):
    id = models.AutoField(primary_key=True)
    # 单采订单
    apheresis_order = models.ForeignKey(verbose_name="单采订单", to=Apheresis_Order,
                                        on_delete=models.CASCADE, db_column="apheresis_order_id")
    # 采血类型 1、血细胞 2、血浆
    apheresis_type_choice = (("血细胞", "血细胞"), ("血浆", "血浆"),)
    apheresis_type = models.CharField(verbose_name="采血类型", choices=apheresis_type_choice, max_length=50)
    # 采血量
    # apheresis_type血细胞 apheresis_volume 写入到 SaleOrderDanCai -- Item1Qty
    # apheresis_type血浆 apheresis_volume 写入到 SaleOrderDanCai -- Item2Qty
    apheresis_volume = models.FloatField(verbose_name="采血量")
    # 采血量单位
    apheresis_volume_unit_choice = (("ml", "ml"), ("L", "L"),)
    apheresis_volume_unit = models.CharField(verbose_name="采血量单位", choices=apheresis_volume_unit_choice, max_length=50)
    trace_mid=models.CharField(verbose_name="追溯中间件", max_length=500,null=True,blank=True)
    trace_name=models.CharField(verbose_name="追溯名称", max_length=500,null=True,blank=True,default='单采血细胞')
    # 标签二维码
    label_qrcode = models.CharField(verbose_name="标签二维码", max_length=500,null=True,blank=True)
    def __str__(self):
        return f"{self.apheresis_order.order_no}-{self.label_qrcode}"
    class Meta:
        verbose_name = '采集订单明细信息'
        verbose_name_plural = '采集订单明细信息'
        ordering =["id"]
        db_table = "Apheresis_Order_Detail"
        

class Apheresis_Order_Attachment(ModelWithLog):
    file_id = models.CharField(verbose_name="文件ID", primary_key=True, max_length=50)
    name = models.CharField(verbose_name="文件名", max_length=500)
    ext = models.CharField(verbose_name="文件后缀", max_length=50)
    size = models.IntegerField(verbose_name="文件大小")
    root_dir = models.CharField(verbose_name="文件根目录", max_length=500,null=True,blank=True)
    file_path = models.CharField(verbose_name="文件路径", max_length=2000)
    file_label_name = models.CharField(verbose_name="订单附件类型名称", max_length=50)
    apheresis_order = models.ForeignKey(verbose_name="订单", to=Apheresis_Order,on_delete=models.CASCADE, db_column="apheresis_order_id")
    last_update = models.DateTimeField(verbose_name="最后更新时间", auto_now=True)
    creater = models.ForeignKey(verbose_name="创建人", to=User,on_delete=models.CASCADE, db_column="creater_id",related_name="apheresis_order_attachment_creater_id",null=True)
    def __str__(self):
        return f"{self.apheresis_order.order_no}-{self.name}"
    class Meta:
        verbose_name = '采集订单附件信息'
        verbose_name_plural = '采集订单附件信息'
        ordering =["file_id"]
        db_table = "Apheresis_Order_Attachment"

# 单采物流信息
class Apheresis_Logistics(ModelWithLog):
    id = models.AutoField(primary_key=True)
    # 单采订单
    apheresis_order = models.OneToOneField(verbose_name="单采订单", to=Apheresis_Order,
                                        on_delete=models.CASCADE, db_column="apheresis_order_id")
    task_id = models.CharField(verbose_name="任务ID", max_length=50,null=True,blank=True)
    # 物流公司外键
    logistics_company = models.ForeignKey(verbose_name="物流公司", to=LogisticsCompany,on_delete=models.CASCADE, db_column="logistics_company_id",null=True,blank=True)
    # 三方物流单号
    logistics_no = models.CharField(verbose_name="三方物流单号", max_length=50)
    logistics_plan_to_hospital = models.DateTimeField(verbose_name="预计到达医院日期",null=True,blank=True)
    # 单采提货确认更新
    logistics_actual_to_hospital = models.DateTimeField(verbose_name="实际到达医院日期",null=True,blank=True) 
    # 增加预计到达医院 日期手填 
    # 医疗机构 从单采订单中获取
    # 增加医院联系人员 来源于单采订单中的 销售订单的创建人 带出电话
    # 预约单采时间 从单采订单中获取 plan_apheresis_date
    logistics_hospital_contact = models.IntegerField(verbose_name="医院联系人员", null=True,blank=True)
    # 物流状态
    logistics_status_choice = (
        ("1", "赶往医院中"),
        ("2", "已到医院"),
        ("3", "赶往仓库中"),
        ("4", "仓库已接收"),
    )
    logistics_status = models.CharField(verbose_name="物流状态", choices=logistics_status_choice,null=True, max_length=50)
    # 物流备注
    logistics_remark = models.CharField(verbose_name="物流备注", max_length=2000,null=True,blank=True)
    # 物流创建人
    creater = models.ForeignKey(verbose_name="创建人", to=User,on_delete=models.CASCADE, db_column="creater_id",related_name="apheresis_logistics_creater_id",null=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    # 0-草稿 可以通过确认按钮编辑所有信息
    # 1-审核中 不可以通过确认、保存按钮编辑所有信息
    # 2-已审核  不可以通过确认、保存按钮编辑所有信息
    status_choice = (
        ("0", "草稿"),
        ("1", "审核中"),
        ("2", "已审核"),
    )
    status=models.CharField(verbose_name="状态",max_length=50,null=True,choices=status_choice)
    def __str__(self):
        return self.apheresis_order.order_no
    def get_logistics_status_display(self):
        if self.status=="2":
            return self.logistics_status_choice[int(self.logistics_status)-1][1]
        else:
            return "预约中"
    class Meta:
        verbose_name = '单采物流信息'
        verbose_name_plural = '单采物流信息'
        ordering =["id"]
        db_table = "Apheresis_Logistics"
        # 单采物流审核权限，反审核权限,拒绝权限
        permissions = (("approve_Apheresis_Logistics", "华东审核"),("re_actavite_Apheresis_Logistics", "华东反审核"),("reject_Apheresis_Logistics", "华东拒绝")
                    )


class Apheresis_Logistics_Detail(ModelWithLog):
    id = models.AutoField(primary_key=True)
    # 单采物流信息
    apheresis_logistics = models.OneToOneField(verbose_name="单采物流信息", to=Apheresis_Logistics,
                                        on_delete=models.CASCADE, db_column="apheresis_logistics_id")
    logistics_no = models.CharField(verbose_name="三方物流单号", max_length=50)
    from_contact_user = models.IntegerField(verbose_name="出发地物流人员",null=True,blank=True)
    from_contact = models.CharField(verbose_name="出发地物流人员", max_length=50,null=True,blank=True)
    from_address = models.CharField(verbose_name="出发地地址", max_length=2000,null=True,blank=True)
    from_tel = models.CharField(verbose_name="出发地联系电话", max_length=50,null=True,blank=True)
    # 从from_address出发时间，单采提货确认更新
    from_address_time_start=models.DateTimeField(verbose_name="揽收人员到达时间",null=True,blank=True)
    # 从from_address出发时间，单采发运更新
    from_address_time_end = models.DateTimeField(verbose_name="揽收人员出发时间",null=True,blank=True)
    # 单采发运更新 from_address_operater
    from_address_operater=models.ForeignKey(verbose_name="出发地操作人", to=User,on_delete=models.CASCADE,db_column="from_address_operater_id",related_name="from_address_operater_id",null=True)
    from_address_remark = models.CharField(verbose_name="出发地备注", max_length=2000,null=True,blank=True)
    to_contact_user = models.IntegerField(verbose_name="目的地物流人员",null=True,blank=True)
    to_contact = models.CharField(verbose_name="目的地联系人", max_length=50,null=True,blank=True)
    to_address = models.CharField(verbose_name="目的地地址", max_length=2000,null=True,blank=True)
    to_tel = models.CharField(verbose_name="目的地联系电话", max_length=50,null=True,blank=True)
    # 到达目的地时间，单采接收的时间更新
    to_address_time = models.DateTimeField(verbose_name="单采到达CMC接收时间",null=True,blank=True)
    to_address_operater=models.ForeignKey(verbose_name="目的地操作人", to=User,on_delete=models.CASCADE,db_column="to_address_operater_id",related_name="to_address_operater_id",null=True)
    to_address_remark = models.CharField(verbose_name="目的地备注", max_length=2000,null=True,blank=True)
    # 状态
    # 0-未生效 单据创建-未审核, 直接修改单据信息。不显示变更、更换按钮
    # 1-已生效 物料审核后，可以提货单确认。 未出发前，可以变更物流信息。
    # 2-单采提货确认 后 出发地物流人员不能改，这时可以更换物料资料(保留旧行，新增新行) ，变更目的地物流人员。
    # 3-单采发运 后 出发地物流人员不能改，这时可以更换物料资料(保留旧行，新增新行) ，变更目的地物流人员。
    # 4-单采接收   这时不显示变更、更换按钮。
    status_choice = (
        ("0", "未生效"),
        ("1", "已生效"),
        ("2", "物流提货"),
        ("3", "单采发运"),
        ("4", "已接收"),
    )
    status = models.CharField(verbose_name="状态", choices=status_choice, max_length=50)
    # 物流备注
    logistics_remark = models.CharField(verbose_name="物流备注", max_length=2000,null=True,blank=True)
    def __str__(self):
        return f"{self.apheresis_logistics.apheresis_order.order_no}-{self.logistics_no}"
    class Meta:
        verbose_name = '单采物流明细信息'
        verbose_name_plural = '单采物流明细信息'
        ordering =["id"]
        db_table = "Apheresis_Logistics_Detail"


# 单采物流物流资料
class Apheresis_Logistics_Material(ModelWithLog):
    id = models.AutoField(primary_key=True)
    # 物流单
    apheresis_logistics = models.ForeignKey(verbose_name="单采物流信息", to=Apheresis_Logistics,
                                        on_delete=models.CASCADE, db_column="apheresis_logistics_id")
    # 物流资料类型
    material_type_choice = (
        ("温度计", "温度计"),
        ("保温箱", "保温箱"),
        ("液氮罐", "液氮罐"),
    )
    material_type = models.CharField(verbose_name="物流资料类型", choices=material_type_choice, max_length=50)
    # 物料
    logistics_material = models.ForeignKey(verbose_name="物流资料ID", to=LogisticsMaterial,
                                        on_delete=models.CASCADE, db_column="logistics_material_id",null=True)
    # 物流资料规格型号
    material_model = models.CharField(verbose_name="规格型号", max_length=500)
    material_sn = models.CharField(verbose_name="物料序列号", max_length=500)
    # 物料备注
    material_remark = models.CharField(verbose_name="物料备注", max_length=2000,null=True,blank=True)
    # 0-已被替换 1-生效
    status=models.BooleanField(verbose_name="状态")
    from_line_id=models.ForeignKey(verbose_name="来源行ID", to="self",on_delete=models.CASCADE,db_column="from_line_id",null=True,blank=True)
    def __str__(self):
        return f"{self.apheresis_logistics.apheresis_order.order_no}-{self.material_sn}"
    class Meta:
        verbose_name = '单采物流资料信息'
        verbose_name_plural = '单采物流资料信息'
        ordering =["id"]
        db_table = "Apheresis_Logistics_Material"