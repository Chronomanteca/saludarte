from django.contrib import admin
from .models import Resident, Relative, MedicationInventory, Prescription, distribution

# Register your models here.


class ResidentAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "site",
        "date_birth",
        "date_joined",
        "eps",     
    )

class RelativeAdmin(admin.ModelAdmin):
    list_display = (        
        "first_name",
        "last_name",
        "kinship",  
        "resident",
    )

class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (   
        "presentation",
        "dosage",
        "dosage_units",        
        "salida_semanal",
        "resident",
    )

class DistributionAdmin(admin.ModelAdmin):
        list_display = (   
        "residente",
        "prescription",
        "hora",
        "dosis_diaria",
        "comentarios",
    )

class MedicationInventoryAdmin(admin.ModelAdmin):
    list_display = ( 
        "residente",  
        "presentation",
        "ammount",
        "delivery_units",
        "date_delivery",
        "reporte_duracion",
    )

    @admin.display(description='Correo')
    def informe_correo(self, obj):
        # in this context, obj is the Manager instance for this line item
        return obj.email()

    @admin.display(description='Residente')
    def residente(self, obj):
        # in this context, obj is the Manager instance for this line item
        return obj.get_resident()

    @admin.display(description='reporte de duracion')
    def reporte_duracion(self, obj):
        # in this context, obj is the Manager instance for this line item
        return obj.calculate_total_span()


admin.site.register(Resident,ResidentAdmin)
admin.site.register(Relative,RelativeAdmin)
admin.site.register(Prescription,PrescriptionAdmin)
admin.site.register(MedicationInventory,MedicationInventoryAdmin)
admin.site.register(distribution,DistributionAdmin)


