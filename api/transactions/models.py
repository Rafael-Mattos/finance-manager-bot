from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    name = models.CharField(max_length=50, verbose_name='Grupo')

    TYPE_CHOICES = [
        ("r", "Receita"),
        ("e", "Despesa"),
    ]
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, 
                            verbose_name='Tipo da Transação')
    
    created_at = models.TimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.TimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        ordering = ['name']
        verbose_name = 'Grupo'
    
    def __str__(self):
        return self.name


class Description(models.Model):
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='Grupo')
    name = models.CharField(max_length=50, verbose_name='Descrição')
    created_at = models.TimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.TimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        ordering = ['group', 'name']
        verbose_name = 'Descrição'
    
    def __str__(self):
        return self.name


class Transactions(models.Model):
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='Grupo')
    description = models.ForeignKey(Description, on_delete=models.PROTECT, 
                                    verbose_name='Descrição')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Usuário')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    obs = models.CharField(max_length=100, null=True, blank=True, 
                           verbose_name='Observação')
    created_at = models.TimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.TimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Lançamento'
    
    def __str__(self):
        return self.description


class Recurring(models.Model):
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='Grupo')
    description = models.ForeignKey(Description, on_delete=models.PROTECT, 
                                    verbose_name='Descrição')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Usuário')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    begin = models.TimeField(verbose_name='Início')
    end = models.TimeField(verbose_name='Final')
    obs = models.CharField(max_length=100, null=True, blank=True, 
                           verbose_name='Observação')
    created_at = models.TimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.TimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        ordering = ['begin']
        verbose_name = 'Lançamento recorrente'
    
    def __str__(self):
        return self.description
