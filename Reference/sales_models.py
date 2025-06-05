import datetime
from django.db import models

from django_extend.base import ModelWithLog
from django_extend.models import User
from master_data.models import Product

# Create your models here.
# 医疗机构
class MedicalInstitution(ModelWithLog):
    id = models.AutoField(primary_key=True)
    institution_code = models.CharField(verbose_name="机构编号", unique=True, max_length=50)
    institution_name = models.CharField(verbose_name="机构名称", max_length=500)
    short_name = models.CharField(verbose_name="机构简称",null=True,blank=True, max_length=200)
    # 预计单采运输时间
    estimated_apheresis_transport_time = models.IntegerField(verbose_name="预计单采运输时间")
    # 预计产品运输时间
    estimated_product_transport_time = models.IntegerField(verbose_name="预计产品运输时间",default=0)
    # 允许单采
    allow_apheresis = models.BooleanField(verbose_name="允许单采")
    # 允许产品输注
    allow_product_transfusion = models.BooleanField(verbose_name="允许产品输注")
    valid_from=models.DateTimeField(verbose_name="有效期开始时间",null=True,blank=True)
    valid_to=models.DateTimeField(verbose_name="有效期结束时间",null=True,blank=True)
    status=models.BooleanField(verbose_name="状态")
    # 增加一个追溯的机构ID
    trace_institution = models.IntegerField(verbose_name="追溯机构ID",null=True,blank=True,db_column="trace_institution_id")
    def __str__(self):
        return self.institution_code + "-" + self.institution_name
    class Meta:
        verbose_name = '医疗机构信息'
        verbose_name_plural = '医疗机构信息'
        ordering =["id"]
        db_table = "MedicalInstitution"
        # 权限组，医疗机构的功能操作权限,退货的权限
        permissions = (("operation_medicalinstitution", "医疗机构的功能操作权限"),("return_medicalinstitution", "医疗机构退货权限"),)

class MedicalInstitutionAddress(ModelWithLog):
    id=models.AutoField(primary_key=True)
    medical_institution=models.ForeignKey(verbose_name="医疗机构", to=MedicalInstitution, on_delete=models.CASCADE, db_column="medical_institution_id")
    address=models.CharField(verbose_name="地址", max_length=500)
    is_default=models.BooleanField(verbose_name="是否默认",default=False)
    def __str__(self):
        return self.medical_institution.short_name if self.medical_institution.short_name else self.medical_institution.institution_name
    class Meta:
        verbose_name = '医疗机构地址信息'
        verbose_name_plural = '医疗机构地址信息'
        ordering =["id"]
        db_table = "MedicalInstitutionAddress"

# 医疗机构的产品授权
class MedicalInstitutionProduct(ModelWithLog):
    id = models.AutoField(primary_key=True)
    medical_institution = models.ForeignKey(verbose_name="医疗机构", to=MedicalInstitution,
                                           on_delete=models.CASCADE, db_column="medical_institution_id")
    product = models.ForeignKey(verbose_name="产品", to=Product,
                                on_delete=models.CASCADE, db_column="product_id")
    def __str__(self):
        return self.medical_institution.institution_code
    class Meta:
        verbose_name = '医疗机构产品授权信息'
        verbose_name_plural = '医疗机构产品授权信息'
        ordering =["id"]
        db_table = "MedicalInstitutionProduct"

# 医疗机构的用户角色授权
class MedicalInstitutionUserRole(ModelWithLog):
    id = models.AutoField(primary_key=True)
    medical_institution = models.ForeignKey(verbose_name="医疗机构", to=MedicalInstitution,
                                           on_delete=models.CASCADE, db_column="medical_institution_id")
    # CART专员、验收员
    role = models.CharField(verbose_name="角色", max_length=50)
    user = models.ForeignKey(verbose_name="用户", to=User,on_delete=models.CASCADE, db_column="user_id",related_name="medical_institution_user")
    def __str__(self):
        return self.medical_institution.institution_code
    class Meta:
        verbose_name = '医疗机构用户角色授权信息'
        verbose_name_plural = '医疗机构用户角色授权信息'
        ordering =["id"]
        db_table = "MedicalInstitutionUserRole"


# DTP药房
class DTP(ModelWithLog):
    id = models.AutoField(primary_key=True)
    dtp_code = models.CharField(verbose_name="DTP编号", unique=True, max_length=50)
    dtp_name = models.CharField(verbose_name="DTP名称", max_length=500)
    short_name = models.CharField(verbose_name="DTP简称", max_length=200)
    start_time=models.DateTimeField(verbose_name="有效期开始时间")
    end_time=models.DateTimeField(verbose_name="有效期结束时间")
    status=models.BooleanField(verbose_name="状态")
    tel = models.CharField(verbose_name="联系电话", max_length=50,null=True,blank=True)
    address = models.CharField(verbose_name="收货地址", max_length=500,null=True,blank=True)
    trace_id=models.CharField(verbose_name="追溯ID", max_length=500,null=True,blank=True)
    # dtp_code 使用追溯Warehouse WarehouseCode
    # trace_warehouseid = models.IntegerField(verbose_name="追溯仓库ID",null=True,blank=True,db_column="trace_warehouseid")
    def __str__(self):
        return self.dtp_code
    
    class Meta:
        verbose_name = 'DTP药房信息'
        verbose_name_plural = 'DTP药房信息'
        ordering =["id"]
        db_table = "DTP"
        # 权限组，DTP药房功能操作权限,退货的权限
        permissions = (("operation_dtp", "DTP药房功能操作权限"),("return_dtp", "DTP药房退货权限"),)

# 商业化产品授权
class ProductUserRole(ModelWithLog):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(verbose_name="产品", to=Product,on_delete=models.CASCADE, db_column="product_id")
    user = models.ForeignKey(verbose_name="用户", to=User,on_delete=models.CASCADE, db_column="user_id",related_name="product_user")
    def __str__(self):
        return self.product.product_code+"_"+self.user.username
    class Meta:
        verbose_name = '商业化产品角色授权信息'
        verbose_name_plural = '商业化产品角色授权信息'
        ordering =["id"]
        db_table = "ProductUserRole"

# 商业化订单
class SalesOrder(ModelWithLog):
    id = models.AutoField(primary_key=True)
    order_no = models.CharField(verbose_name="订单编号", unique=True, max_length=50)
    medical_institution = models.ForeignKey(verbose_name="医疗机构", to=MedicalInstitution,
                                            on_delete=models.CASCADE, db_column="medical_institution_id")
    medical_address = models.CharField(verbose_name="医疗机构地址", max_length=2000,null=True,blank=True)
    product = models.ForeignKey(verbose_name="产品", to=Product,
                                on_delete=models.CASCADE, db_column="product_id")
    # 订单状态
    order_status_choice = (
        ("草稿", "草稿"), # 保存数据没提交
        ("待审核", "待审核"),# 提交事件完成
        ("已审核", "已审核"),# 华东审核事件完成
        ("等待输注", "等待输注"),# 单采流程完成 
        ("完成输注", "完成输注"),# 第一次输注完成
        ("关闭", "关闭"),# 第一次输注完成
    )
    order_status = models.CharField(verbose_name="订单状态", choices=order_status_choice, max_length=50)
    # 患者编号
    patient_code = models.CharField(verbose_name="患者编号", max_length=50)
    # 患者姓名
    patient_name = models.CharField(verbose_name="患者姓名", max_length=50)
    # 患者姓名缩写
    patient_name_abb = models.CharField(verbose_name="患者姓名缩写", max_length=50)
    # 患者性别
    gender=models.CharField(verbose_name="性别", max_length=50,db_column="gender")
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
    id_type = models.CharField(verbose_name="证件类型", choices=id_type_choice, max_length=50)
    # 证件号码
    id_number = models.CharField(verbose_name="证件号码", max_length=50,null=True,blank=True)
    id_number_aes = models.CharField(verbose_name="证件号码",max_length=200,null=True,blank=True)
    remark = models.CharField(verbose_name="备注", max_length=2000,null=True,blank=True)
    creater = models.ForeignKey(verbose_name="创建人", to=User,on_delete=models.CASCADE, db_column="creater_id",related_name="sales_order_creater")
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    # DonorInfo 华东审核完成写入供者信息
    donor_info = models.IntegerField(verbose_name="供者信息", db_column="donor_info_id",null=True,blank=True)
    task_id = models.CharField(verbose_name="任务ID", max_length=50,null=True,blank=True)
    order_date = models.DateField(verbose_name="订单日期",default=datetime.date.today,null=True,blank=True)
    is_deleted = models.BooleanField(verbose_name="是否删除",default=False)
    is_closed = models.BooleanField(verbose_name="是否关闭",default=False)
    trace_node_json = models.TextField(verbose_name="追溯节点信息",null=True,blank=True)
    order_type_choice = (
        ("1", "标准订单"),
        ("2", "择期订单"),
    )
    order_type = models.CharField(verbose_name="订单类型", choices=order_type_choice, max_length=50,null=True,blank=True)
    delayed_status_choice = (
        ("1", "标准订单"),
        ("2", "待择期"),
        ("3", "择期确认"),
    )
    delayed_status = models.CharField(verbose_name="择期状态", choices=delayed_status_choice, max_length=50,null=True,blank=True)
    delayed_aps_task_id = models.ForeignKey(verbose_name="APSTaskID", to="aps_app.ApsTask",on_delete=models.SET_NULL, db_column="delayed_aps_task_id",null=True,blank=True)
    delayed_task_id = models.IntegerField(verbose_name="择期任务ID",null=True,blank=True)
    def __str__(self):
        return self.order_no
    class Meta:
        verbose_name = '商业化订单信息'
        verbose_name_plural = '商业化订单信息'
        ordering =["id"]
        db_table = "SalesOrder"
        # 文件打包下载权限
        permissions = (("close_salesorder", "关闭销售订单"),("re_actavite_salesorder", "反审核销售订单"),("huadong_check_salesorder", "华东审核"),("filedownload_salesorder", "文件打包下载(销售订单)"),("delayed_confirm_salesorder", "申请生产"),)


class SaleOrderAttachment(ModelWithLog):
    file_id = models.CharField(verbose_name="文件ID", primary_key=True, max_length=50)
    name = models.CharField(verbose_name="文件名", max_length=500)
    ext = models.CharField(verbose_name="文件后缀", max_length=50)
    size = models.IntegerField(verbose_name="文件大小")
    root_dir = models.CharField(verbose_name="文件根目录", max_length=500,null=True,blank=True)
    file_path = models.CharField(verbose_name="文件路径", max_length=2000)
    file_label_name = models.CharField(verbose_name="订单附件类型名称", max_length=50)
    sale_order = models.ForeignKey(verbose_name="订单", to=SalesOrder,on_delete=models.CASCADE, db_column="sale_order_id")
    last_update = models.DateTimeField(verbose_name="最后更新时间", auto_now=True)
    creater = models.ForeignKey(verbose_name="创建人", to=User,on_delete=models.CASCADE, db_column="creater_id",related_name="sale_order_attachment_creater_id",null=True)
    def __str__(self):
        return f"{self.sale_order.order_no}-{self.name}"
    class Meta:
        verbose_name = '商业化订单附件信息'
        verbose_name_plural = '商业化订单附件信息'
        ordering =["file_id"]
        db_table = "SaleOrderAttachment"