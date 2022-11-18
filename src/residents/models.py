from contextlib import nullcontext
from datetime import date, timedelta
from email.policy import default

from accounts.models import Site, User
from core.models import Person
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models import Sum
from django.urls import reverse_lazy
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from medications.models import Presentation


class Resident(Person):
    """
    It draws the information of the resident of the organization.
    """

    # Person model includes:
    # first_name, last_name, identification_type, identification_number,

    site = models.ForeignKey(
        Site,
        verbose_name="sede",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
    )

    date_birth = models.DateField(
        "fecha de nacimiento",
        blank=True,
        null=True,
    )

    date_joined = models.DateField(
        "fecha de ingreso",
        default=timezone.now,
        blank=True,
        null=True,
    )

    eps = models.CharField(
        "EPS",
        max_length=128,
        blank=True,
    )

    """
    Overriding onSave method so it creates a placeholder relative "Saludarte" as an auxiliary relative for certain tasks in the application
    """
    def save(self, *args, **kwargs):
        if not self.pk:
            # This code only happens if the objects is
            # not in the database yet. Otherwise it would
            # have pk
            

            super(Resident, self).save(*args, **kwargs)
            Relative(first_name="Saludarte", last_name ="Gestion", identification_type = 1,identification_number = 00000,resident = self).save()

    def get_full_name(self):
        return self.first_name + " " +self.last_name

    def __str__(self):
        return self.first_name + " " +self.last_name

    #Reestructurando funcion
    def get_inventory_info(self):
        prescription_set = Prescription.objects.filter(resident = self)
        inventory_entries = MedicationInventory.objects.filter(resident = self)
        entries_total = inventory_entries.values("presentation").annotate(total_cantidad = Sum(('ammount')))
        for e in entries_total :
            pr = Presentation.objects.get(pk = e.get("presentation")) 
            inv = inventory_entries.filter(presentation = e.get("presentation")).latest("date_delivery")
            try:
                pres = prescription_set.filter(presentation = pr).latest("date_delivery")
            except ObjectDoesNotExist:
                pres = Prescription(resident = self, dosage = 0, dosage_units = 0)
                

            e["name"] = pr.__str__()
            e["dosage"] = pres.get_full_dosage()
            e["total_cantidad"] = str(e.get("total_cantidad"))+" "+str(inv.get_delivery_unit())    
            e["salidas_semanales"] = pres.salida_semanal()   
            try:
                loan = Loan.objects.get(presentation = pr)  
                e["deuda"] = loan.get_full_loan()
            except ObjectDoesNotExist:
                e["deuda"] = "0 N/A"

            
        return entries_total

    class Meta:
        verbose_name = "Residente"
        verbose_name_plural = "Residentes"

    def get_absolute_url(self):
        return reverse_lazy("residents:detail", kwargs={"pk": self.pk})


SPOUSE = 1
PARENT = 2
SIBLING = 3
CHILD = 4
GRANDPARENT = 5
RELATIVE = 6
FRIEND = 7
OTHER = 8

KINSHIP_CHOICES = (
    (SPOUSE, "Cónyuge"),
    (PARENT, "Padre / Madre"),
    (SIBLING, "Hermano / Hermana"),
    (CHILD, "Hijo / Hija"),
    (GRANDPARENT, "Abuelo / Abuela"),
    (RELATIVE, "Familiar"),
    (FRIEND, "Amigo / Allegado"),
    (OTHER, "Otro"),
)


class Relative(Person):
    """
    It represents a relative of a resident associated via a kinship.
    """

    # Person model includes:
    # first_name, last_name, identification_type, identification_number, gender

    kinship = models.SmallIntegerField(
        "parentesco",
        choices=KINSHIP_CHOICES,
        default = OTHER,
        null=False,
        blank=False,
    )

    email = models.EmailField(
        "correo electrónico",
        max_length=255,
        blank=True,
    )

    contact_number = models.CharField(
        "número de contacto",
        max_length=32,
        blank=True,
    )

    email_alerts = models.BooleanField(
        "alertas por correo electrónico",
        default=False,
    )

    whatsapp_alerts = models.BooleanField(
        "alertas por WhatsApp",
        default=False,
    )

    resident = models.ForeignKey(
        Resident,
        verbose_name="familiares residentes",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )

    def __str__(self):
        return self.first_name+" "+self.last_name

    class Meta:
        verbose_name = "Familiar"
        verbose_name_plural = "Familiares"

    def get_absolute_url(self):
        return (
            reverse_lazy("residents:detail", kwargs={"pk": self.resident.pk})
            + "?page=2"
        )


HOURS = 1
DAYS = 2
WEEKS = 3
MONTHS = 4
FREQUENCY_UNIT_CHOICES =(
    (HOURS,"horas"),
    (DAYS,"dias"),
    (WEEKS,"semanas"),
    (MONTHS,"meses"),
)

NONE = 0
MG = 1
ML = 2
DROPS = 3
MG_ML = 4
TABLET = 5
CAPSULE = 6
PILL = 7
DROPS = 8
SYRUP = 9
INJECTION = 10

PRESCRIPTION_DOSAGE_UNIT_CHOICES = (
    (NONE,"N/A"),
    (MG, "mg"),
    (ML, "ml"),
    (MG_ML, "mg_ml"),
    (TABLET, "Tabletas"),
    (CAPSULE, "Cápsulas"),
    (PILL, "Pastillas"),
    (DROPS, "Gotas"),
    (SYRUP, "Jarabe"),
    (INJECTION, "Inyección"),

)


class Prescription(models.Model):
    """
    Represents the resident's prescription of a given presentation for a medication.
    """

    """
    agregar encargado (se captura del user)
    Cambio basado en calculo de distribution
    date ingreso
    """
    dosage = models.FloatField(
        "dosis",
        blank=False,
        default=0,
    )
    dosage_units = models.SmallIntegerField(
        "unidad de dosis",
        blank =False,
        null=True,
        default = 0,
        choices= PRESCRIPTION_DOSAGE_UNIT_CHOICES,
    )

    resident = models.ForeignKey(
        Resident,
        verbose_name="residente",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    presentation = models.ForeignKey(
        Presentation,
        verbose_name="presentacion",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    responsible = models.ForeignKey(
        User,
        verbose_name="responsable",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )  

    date_delivery = models.DateTimeField(
        "fecha de recepcion",
        default=timezone.now,
        blank=True,
        null=True,
    ) 
    
    def get_full_dosage(self):        
        return str(self.dosage)+" "+self.get_dosage_units_display()

    def get_resident(self):
        return self.resident.__str__()    

    def get_presentation_list(self):
        return Presentation.objects.all()
    
    def get_presentation(self):
        return self.presentation.__str__()

    def salida_semanal(self):
        return str(self.get_weekly_issues())

    def get_responsible(self):

        print(self.responsible.get_full_name())
        return self.responsible

    def get_distributions(self):
        dist = Distribution.objects.filter(prescription = self)
        return dist

    def get_weekly_issues(self):
        """
        dosage is daily
        so, weekly duration is dosage * 7
        """
        return str(self.dosage * 7) +" "+ self.get_dosage_units_display()

    def get_dosage_unit(self):
        return self.get_dosage_unit    

    def get_frequency(self):
        return self.frequency


    def get_dosage(self):
        return self.dosage

    def __str__(self): 
        msg = self.resident.__str__()+" "+self.presentation.__str__()+" , administrar  "+str(self.dosage)+" "+self.get_dosage_units_display()    
        return msg
    
    """
    Overriding onSave method so it creates a blank inventory entry signifying that there should be future entries for this prescription
    """
    def save(self, *args, **kwargs):
            # This code only happens if the objects is
            # not in the database yet. Otherwise it would
            # have pk
            
            super(Prescription, self).save(*args, **kwargs)
            rel = Relative.objects.get(first_name = "Saludarte",resident = self.resident)
            print(rel)
            MedicationInventory(resident = self.resident, relative = rel,presentation = self.presentation, delivery_units = self.dosage_units,ammount = 0,comentarios = "Registro generado automaticamente por la plataforma").save()

    class Meta:
        verbose_name = "Prescripcion"
        verbose_name_plural = "Prescripciones"

    def get_absolute_url(self):
        return (
            reverse_lazy("residents:detail", kwargs={"pk": self.resident.pk})
            + "?page=3")
    

FAST = 1
MORNING = 2
NOON = 3
EVENING = 4

DISTRIBUTION_HOUR_CHOICES = (
    (FAST, "Ayuno"),
    (MORNING, "Mañana"),
    (NOON, "Tarde"),
    (EVENING, "Noche"),
)

class Distribution(models.Model):

    prescription = models.ForeignKey(
        Prescription,
        verbose_name="prescripcion",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )  

    hora = models.SmallIntegerField(
        "hora",
        choices=DISTRIBUTION_HOUR_CHOICES,
        null=False,
        default = 1,
        blank=False,
    )

    dosis_diaria = models.FloatField(
        "dosis diaria",
        blank = False
    )    
    
    comentarios = models.TextField(
        "comentarios",
        max_length=512,
        blank=True,
        null=True,
    )  

    class Meta:
        verbose_name = "Distribucion"
        verbose_name_plural = "Distribuciones"   

    def __str__(self):
        #msg =self.prescription.__str__()+" dar "+str(self.dosis_diaria)+" "+self.prescription.get_dosage_units_display()+" en la "+self.get_hora_display()
        msg = str(self.id)
        return msg


INPUT = 1
OUTPUT=2
LOAN=3
LOAN_PAYMENT = 4

INVENTORY_CONCEPT_CHOICES = (
    (INPUT, "Entrada de inventario"),
    (OUTPUT, "Salida de inventario"),
    (LOAN, "Prestamo"),
    (LOAN_PAYMENT, "Pago de Prestamo"),
)

#This class actually represents an entry inside the resident's medication,
class MedicationInventory(models.Model):


    resident = models.ForeignKey(
        Resident,
        verbose_name="residente",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    relative = models.ForeignKey(
        Relative,
        verbose_name="familiar",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    presentation = models.ForeignKey(
        Presentation,
        verbose_name="presentacion",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )  

    ammount = models.IntegerField(
        "cantidad",
        blank = False,
        null=True,
    )  

    delivery_units = models.SmallIntegerField(
        "unidad",
        blank =False,
        null=True,
        default = 0,
        choices= PRESCRIPTION_DOSAGE_UNIT_CHOICES,
    )  

    date_delivery = models.DateTimeField(
        "fecha de recepcion",
        default=timezone.now,
        blank=True,
        null=True,
    )        

    comentarios = models.TextField(
        "comentarios",
        max_length=512,
        default = "Niguno",
        blank=True,
        null=True,
    )

    concept = models.SmallIntegerField(
        "concepto",
        blank =False,
        null=True,
        default = 1,
        choices= INVENTORY_CONCEPT_CHOICES,
    )  

    responsible = models.ForeignKey(
        User,
        verbose_name="responsable",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )  

    def get_date(self):
        date_time_str = self.date_delivery.strftime("%Y-%m-%d %H:%M:%S")
        return date_time_str


    def get_resident(self):
        return self.resident.__str__()  

    def get_delivery_unit(self):
        return self.get_delivery_units_display()

    def get_prescription_dosage(self):
        pres = Prescription.objects.filter(resident = self.resident).get(presentation = self.presentation)        
        return pres.get_full_dosage()

    def get_presentation(self):
        return self.presentation.__str__()   

    def get_weekly_issues(self):
        pres = Prescription.objects.filter(resident = self.resident).get(presentation = self.presentation)      
        return  pres.get_weekly_issues()    

    def get_full_ammount(self):
        return str(self.ammount)+" "+self.get_delivery_units_display()

    def get_ammount_calculated(self):
        entradas = MedicationInventory.objects.filter(resident = self.resident)

        totales = entradas.values("presentation").annotate(total_cantidad = Sum(('ammount')))
        print(totales)
        return 0
    
    #Overriding save function in order to check if an entry needs to pay a medication loan
    def save(self, *args, **kwargs):
        # This code only happens if the objects is
        # not in the database yet. Otherwise it would
        # have pk            
        super(MedicationInventory, self).save(*args, **kwargs)
        presentation = self.presentation
        try:       
            loan = Loan.objects.get(presentation = presentation)     
            if self.concept == 1 and loan.ammount_loan > 0:
                print("TENEMOS DEUDA")
                
                rel = Relative.objects.get(first_name = "Saludarte",resident = self.resident)
                
                print("ajustando deudas")
                #decreasing ammount of debt
                payment = loan.ammount_loan - self.ammount

                if payment>0:                                       
                    inv_comentarios = "Se usaron "+str(self.ammount)+" para pagar el prestamo de "+str(loan.ammount_loan)
                    MedicationInventory(resident = self.resident, presentation = presentation, ammount = -self.ammount, responsible = self.responsible, relative = rel, delivery_units = self.delivery_units, concept = 4, comentarios = inv_comentarios).save()
                    loan.ammount_loan = loan.ammount_loan - self.ammount
                    loan.save()
                else:
                    new_payment = abs(payment)
                    inv_comentarios = "Se usaron "+str(self.ammount - new_payment)+" para pagar el prestamo de "+str(loan.ammount_loan)
                    MedicationInventory(resident = self.resident, presentation = presentation, ammount = -(self.ammount - new_payment), responsible = self.responsible, relative = rel, delivery_units = self.delivery_units, concept = 4, comentarios = inv_comentarios).save()
                    loan.ammount_loan = 0
                    loan.save()

        except ObjectDoesNotExist:
            print("no tengo deuda")



            
        
    """
    def email(self):
        subj = "informe de duracion de medicamentos de "+self.resident.__str__()
        msg = "El Residente "+self.resident.__str__()+" tiene  "+str(self.ammount)+" "+self.get_delivery_units_display()+" de "+self.presentation.__str__()+". "+self.calculate_total_span()       
       # self.email_test(msg,subj)
        return "correo enviado"
    """


    def __str__(self):
        msg = self.presentation.__str__()
        return msg

    def get_email_list(self):
        relatives = Relative.objects.filter()
        return 0


    def email_test(self,str,subj):
        print("enviando mail")
        subject = "asdasdasd"
        message = str
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ["danisan98@hotmail.es"]        
        #send_mail(subject, message, email_from, recipient_list)


    def calculate_total_span(self):        
        prescription = Prescription.objects.filter(presentation_id = self.presentation.pk).first()    
        if(prescription==None):
            dosis_diaria = 0
        else:            
            dosis_diaria = prescription.get_dosage() 
        fecha_inicio = date(2022,9,1)
        fecha_fin = date(2022,9,20)
        dias_rango = (fecha_fin-fecha_inicio).days        
        dosis_rango = dosis_diaria*(dias_rango+1)
        cantidad_final = self.ammount - dosis_rango
        msg = "entre "+str(fecha_inicio) +" y "+str(fecha_fin)+" Cuando pasen "+ str(int(dias_rango)+1)+" dias, se consumiran "+str(dosis_rango)+" "+self.get_delivery_units_display()+","
        if(cantidad_final<0):
            msg+=" para entonces haran falta: "+str(abs(cantidad_final))+" "+self.get_delivery_units_display()
        elif(cantidad_final==0):
            msg+=" para entonces se acabara el inventario de este medicamento: "
        else:
            msg+=" para entonces sobraran : "+str(cantidad_final)+" "+self.get_delivery_units_display()
        return msg

    class Meta:
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"

    def get_absolute_url(self):
        return (
            reverse_lazy("residents:detail", kwargs={"pk": self.resident.pk})
            + "?page=4"
        )


class Loan(models.Model):

    resident = models.ForeignKey(
        Resident,
        verbose_name="residente",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    presentation = models.ForeignKey(
        Presentation,
        verbose_name="presentacion",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
    )     

    ammount_loan = models.IntegerField(
        "prestamo",
        blank = False,
        null=True,
    )

    loan_units = models.SmallIntegerField(
        "unidad",
        blank =False,
        null=True,
        default = 0,
        choices= PRESCRIPTION_DOSAGE_UNIT_CHOICES,
    )     

    def get_full_loan(self):
        return str(self.ammount_loan)+" "+self.get_loan_units_display()