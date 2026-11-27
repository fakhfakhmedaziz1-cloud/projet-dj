from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Appointment(models.Model):

    # Statut du rendez-vous
    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "En attente"),
            ("CONFIRMED", "Confirmé"),
            ("CANCELLED", "Annulé"),
        ],
        default="PENDING"
    )

    # Motif du rendez-vous
    reason = models.TextField(max_length=255)

    # Prescription médicale
    prescription = models.FileField(
        upload_to="prescriptions/",
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf"],
                message="Accepte uniquement des fichiers PDF."
            )
        ]
    )

    # Durée du rendez-vous en minutes
    duration_minutes = models.PositiveIntegerField(
        default=30
    )

    # Dates de création et de modification
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # Médecin associé au rendez-vous
    doctor = models.ForeignKey(
        "AccountApp.Doctor",
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    # Patient associé au rendez-vous
    patient = models.ForeignKey(
        "AccountApp.Patient",
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    # Date du rendez-vous
    appointment_date = models.DateField()

    def clean(self):
        super().clean()

        if self.appointment_date:

            # Vérifier si le rendez-vous est nouveau
            is_new = self.pk is None

            # Vérifier si la date a changé
            date_changed = True

            if not is_new:
                old_appointment = Appointment.objects.get(
                    pk=self.pk
                )

                date_changed = (
                    old_appointment.appointment_date
                    != self.appointment_date
                )

            # Valider la date uniquement si elle a changé
            if is_new or date_changed:

                if self.appointment_date <= timezone.localdate():
                    raise ValidationError({
                        "appointment_date":
                        "La date du rendez-vous doit être dans le futur."
                    })

    class Meta:

        ordering = ["appointment_date"]

        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "appointment_date"],
                name="unique_doctor_appointment_date",
                violation_error_message=(
                    "Un seul rendez-vous par médecin et par date."
                )
            )
        ]