# vim:sw=4:et:

import gtk
import diacanvas
from gaphor.plugin import Action


class SVGExportAction(Action):

    def update(self):
        tab = self.get_window().get_current_diagram_tab()
        self.sensitive = tab and True or False

    def execute(self):
        filename = (self.get_window().get_current_diagram().name or 'export') + '.svg'
        if gtk.pygtk_version < (2, 4, 0):
            filesel = gtk.FileSelection('Export diagram to SVG file')
            filesel.set_filename(filename)
        else:
            filesel = gtk.FileChooserDialog(title='Export diagram to SVG file',
                                            action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
            filesel.set_current_name(filename)


        response = filesel.run()
        filename = filesel.get_filename()
        filesel.destroy()
        if response == gtk.RESPONSE_OK:
            if filename and len(filename) > 0:
                log.debug('Exporting SVG image to: %s' % filename)
                canvas = self.get_window().get_current_diagram_tab().get_canvas()
                export = diacanvas.ExportSVG()
                try:
                    export.render (canvas)
                    export.save(filename)
                except Exception, e:
                    log.error('Error while saving model to file %s: %s' % (filename, e))

