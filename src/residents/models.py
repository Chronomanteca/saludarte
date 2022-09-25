from contextlib import nullcontext
from importlib.metadata import distribution
from django.db import models
from django.urls import reverse_lazy
from core.models import Person
from django.utils import timezone
from accounts.models import Site
from medications.models import Presentation
from django.core.mail import send_mail
from django.conf import settings

from datetime import date,timedelta


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

    def __str__(self):
        return self.first_name + " " +self.last_name

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
        null=False,
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

MG = 1
ML = 2
DROPS = 3
MG_ML = 4

PRESCRIPTION_DOSAGE_UNIT_CHOICES = (
    (MG, "mg"),
    (ML, "ml"),
    (DROPS , "gotas"),
    (MG, "mg_ml"),

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

    def get_resident(self):
        return self.resident.__str__()

    def salida_semanal(self):
        return str(self.get_weekly_issues())

    def get_weekly_issues(self):
        """
        dosage is daily
        so, weekly duration is dosage * 7
        """
        return self.dosage * 7

    def get_dosage_unit(self):
        return self.get_dosage_unit    

    def get_frequency(self):
        return self.frequency


    def get_dosage(self):
        return self.dosage

    def __str__(self):   
        msg = self.presentation.__str__()+" , administrar  "+str(self.dosage)+" "+self.get_dosage_units_display()    
        return msg


    class Meta:
        verbose_name = "Prescripcion"
        verbose_name_plural = "Prescripciones"

    def get_absolute_url(self):
        return (
            reverse_lazy("residents:detail", kwargs={"pk": self.resident.pk})
            + "?page=3")

    def save(self, *args, **kwargs):

        resident = self.resident
        presentation = self.presentation
        ammount = 0
        delivery_units = self.dosage_units
        MedicationInventory.objects.update_or_create(resident = resident, presentation = presentation, ammount = ammount,delivery_units = delivery_units)        
        super(Prescription, self).save(*args, **kwargs)

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

class distribution(models.Model):

    """
    Aqui mover residente
    Horario : Ayuno (a,m,t)
    presentacionId (foranea)
    Prescripcion X (idForanea)
    dosis_horario (1) pastilla; (30) gotas
    indicaciones: 2 horas antes del ayuno... 30 gotas en... (comentarios)
    """

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

    def residente(self):
        return self.prescription.get_resident()

    class Meta:
        verbose_name = "Distribucion"
        verbose_name_plural = "Distribuciones"   

    def __str__(self):        
        return self.prescription.__str__()+" dar "+str(self.dosis_diaria)+" "+self.prescription.get_dosage_units_display()+" en la "+self.get_hora_display()


class MedicationInventory(models.Model):

    """
    1 presentacion (foreign)
    cantidad (int)
    comentarios (opcional)
    fecha ingreso
    relative
    encargado/a

    ej:
    clonazepam 100mg pastillas
    llegaron 30 pastillas (complementar con presentation_type) (tentativo)
    comentarios: todo ok
    """     

    """
    1 Inventario puede tener muchas entradas de presentaciones
    encargado (get from user)
    

    *
    * Corregir modulo (distribucion agregar presentacion en lugar de prescripcion)
    * notificaciones correo
    * viernes!!
    * valores faltantes


    TODO: prediccion basada en rango entre fecha inicial y fecha final
    """

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
        blank=True,
    )  

    ammount = models.IntegerField(
        "cantidad",
        blank = True
    )  

    delivery_units = models.SmallIntegerField(
        "unidad",
        blank =True,
        null=True,
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
        blank=True,
        null=True,
    )

    def get_resident(self):
        return self.resident.__str__()                           
        

    def email(self):
        subj = "informe de duracion de medicamentos de "+self.resident.__str__()
        msg = "El Residente "+self.resident.__str__()+" tiene  "+str(self.ammount)+" "+self.get_delivery_units_display()+" de "+self.presentation.__str__()+". "+self.calculate_total_span()       
        self.email_test(msg,subj)
        return "correo enviado"


    def __str__(self):
        subj = "informe de duracion de medicamentos de "+self.resident.__str__()
        msg = "El Residente "+self.resident.__str__()+" tiene  "+str(self.ammount)+" "+self.get_delivery_units_display()+" de "+self.presentation.__str__()+". "+self.calculate_total_span()       
        self.email_test(msg,subj)
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