# Stereotypes

In UML, stereotypes are way to extend the application of the UML language to
new domains. For example: SysML started as a profile for UML.

Gaphor supports stereotypes too. They're *the* way for you to adapt your models
to your specific needs.

The UML, SysML, RAAML and other models used in Gaphor – the code is 
generated from Gaphor model files – make use of stereotypes to provide
specific information used when generating the data model code.

To create a stereotype, ensure the UML Profile is active and open the *Profile*
section of the toolbox. First add a *Metaclass* to your diagram. Next add a
*Stereotype*, and connect both with a *Extension*.
The `«metaclass»` stereotype will only show once the *Extension* is connected
both class and stereotype.

```{note}
The class names in the metaclass should be a class name from the UML model,
such as `Class`, `Interface`, `Property`, `Association`.
Or even `Element` if you want to use the stereotype on all elements.
```

Your stereotype declaration may look something like this:

```{diagram} profile
:model: stereotypes
```

The `Asynchronous` stereotype has a property `priority`. This property can
be proved a value once the stereotype is applied to a *Property*, such as an
association end.

When a stereotype can be applied to a model element, a *Stereotype* section
will appear in the editor.

![Stereotype usage example](images/stereotype-usage.png)
