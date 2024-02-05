import ltk
from random import randrange
from control_widget import *
from isoweaves import *
# File save support
import io
from js import Uint8Array, File, URL

# Todo:
# - add save to svg, wif?
#    - https://pyscript.recipes/2024.1.1/basic/file-download/
# - add library


# For debugging purposes
#ltk.window.document.currentScript.terminal.resize(60, 12)
#def print(*args):
#    ltk.find("body").append(" ".join(str(a) for a in args), "<br>")


class MyISO_control_widget(ISO_control_widget):
    """
    Subclassed to locally override:
     - structure_changed()
    """
    def __init__(self, iso_object, idx, initial_values):
        super().__init__(iso_object, idx, initial_values)

    def structure_changed(self):
        # allow us to call functions in this scope
        self.iso_object.changed()


class ISO_widget(object):
    """
    Top level object that manages the complex interrelationships
    of the iso values and corresponding widgets.
    """
    def __init__(self, dimensions=[400,400], initial_values = [[10],[1,1],[1],[0]]):
        # widgets and values
        self.frst_widget = MyISO_control_widget(self, 1, initial_values[0])
        self.scnd_widget = MyISO_control_widget(self, 2, initial_values[1])
        self.thrd_widget = MyISO_control_widget(self, 3, initial_values[2])
        self.frth_widget = MyISO_control_widget(self, 4, initial_values[3])
        # disable frth as plainweave initialisation
        self.frth_widget.disable_buttons(True)
        # make scnd similar visually to total_shafts
        self.scnd_widget.addClass("shaft_lock_box")
        #
        self.total_shafts = 2
        self.lock_shafts = False
        self.lock_widget = None  # will make it soon
        #
        self.ref = []  # used to avoid excessive redraws
        # saved states for Plain(10,11), Twill(20,21), Satin(30,31)
        # - holds [thrd, frth]
        self.plain_state = []
        self.twill_state = []
        self.satin_state = []
        # setup style params
        self.label = "10-01 01-01-00"
        self.dimensions = dimensions  # SVG dimensions
        self.repeats = 2#.2  # repeats to show in SVG
        self.box_min = 20  # min box size in SVG
        self.box_dim = 10  # will be calculated to fit self.dimensions. Use for highlighting
        self.colors = ['red','grey']  # default colors can be overwritten to black/black

    def get_control(self, idx):
        """
        Get the correct control widget by index.
        Used by: disable/enable_parts() and set_iso_pattern()
          to modify the right iso_part.
        """
        parts = [self.frst_widget, self.scnd_widget,
                 self.thrd_widget, self.frth_widget]
        return parts[idx-1]

    def check_alter_frth(self):
        """
        Its possible that any numbers in frth are now too big
        because total_shafts has been adjusted
        """
        newvalues = [f"{min(int(val),self.total_shafts-1)}" for val in self.frth_widget.values]
        if newvalues != self.frth_widget.values:
            self.frth_widget.set_values(newvalues)

    def update_UI_shaft_count(self):
        """
        Sets the shaftcount UI widget to value stored in this class.
        Used by:
        - btninc,btndec,randomcontrol, alter_shafts
        """
        if not self.lock_widget:
            self.lock_widget = ltk.find_list(".shaftin")[0]
        self.lock_widget.val("%02d" % (self.total_shafts))
        # its possible that any numbers in frth are now too big
        self.check_alter_frth()

    def alter_shafts(self, slot, oldvalue, newvalue):
        """
        Called by UI changes to: scnd
        If locked:
         - try to adjust number as desired (by inc/dec other numbers)
        else
         - simply update shafts UI and total_shafts
        """
        if not self.lock_shafts:
            newvalue = max(1, newvalue)
            self.scnd_widget.values[slot] = f"{newvalue:02d}"
            self.total_shafts = self.total_shafts+newvalue-oldvalue
            self.update_UI_shaft_count()
            return newvalue
        else:  # shaft count locked
            new_total = sum(int(input.val()) for input in self.scnd_widget.items)
            correct_total = sum(int(i) for i in self.scnd_widget.values)
            #print("Locked(in change)", slot, new_total, self.scnd)
            # is it even possible
            if len(self.scnd_widget.values) == self.total_shafts:
                # its all 1's. no change possible
                newvalue = 1
            else:  # change is possible
                # increase or decrease
                # slot is the one changed (and will get return value)
                count = correct_total - new_total
                #print(f"..newtotal: {oldvalue} {newvalue} idx={slot} {count}")
                slots = ltk.find_list("#control-2 .ltk-input")
                if newvalue == 0 or oldvalue == 0:
                    newvalue = 1
                    #print("!new/old=0", newvalue,oldvalue)
                elif count > 0:
                    possibles = list(range(len(self.scnd_widget.values)))
                    possibles.remove(slot)  # the possible slots to adjust
                    #print("-add to slots",count,possibles)
                    while count > 0:
                        idx = possibles[randrange(0, len(possibles))]
                        slots[idx].val(f"{int(slots[idx].val())+1:02d}")
                        count -= 1
                    self.scnd_widget.values = [f"{int(input.val()):02d}" for input in slots]
                elif count < 0:
                    possibles = [i for i in range(len(self.scnd_widget.values)) if int(slots[i].val()) != 1]
                    possibles.remove(slot)  # the possible slots to adjust
                    #print("-sub from slots",count,possibles)
                    if possibles:
                        while count < 0:
                            idx = possibles[randrange(0, len(possibles))]
                            slots[idx].val(f"{int(slots[idx].val())-1:02d}")
                            count += 1
                    else:  # no slots can be changed
                        newvalue = oldvalue
                        #print("!nochange", newvalue)
                        slots[slot].val(f"{newvalue:02d}")
                    #
                    self.scnd_widget.values = [f"{int(input.val()):02d}" for input in slots]
             # return newvalue for the initiating slot.
            return newvalue

    def disable_part(self, iso_part=4, rand=False):
        """
        Disable the control inc/dec and random? buttons.
        """
        control = self.get_control(iso_part)
        control.disable_buttons(rand)

    def enable_part(self, iso_part=4, rand=False):
        """
        Enable the control inc/dec and random buttons.
        """
        control = self.get_control(iso_part)
        control.enable_buttons(rand)

    def save_state(self):
        """
        Save the state when switching between plain/twill/satin
         - holds [thrd, frth]
        """
        # make a copy to record unchanging values
        state = [[v for v in self.thrd_widget.values],
                 [v for v in self.frth_widget.values]]
        mode = self.frst_widget.values[0][0]  # 1,2,3 plain,twill,satin
        #print("!",self.frst_widget.values)
        if mode == "1":
            self.plain_state = state
        elif mode == "2":
            self.twill_state = state
        else:  # satin
            self.satin_state = state

    def create_label(self):
        msg = self.frst_widget.values[0] + "-"
        msg += " ".join(self.scnd_widget.values) + "-"
        msg += " ".join(self.thrd_widget.values) + "-"
        msg += " ".join(self.frth_widget.values)
        return msg

    def changed(self, force=False):
        """
        User has changed one or more values. Redraw as required.
        - check for unneccessary spurious changes in this imperfect world.
        """
        redraw = False
        # create a state to check changes against
        ref_state = []
        for el in [self.frst_widget, self.scnd_widget, self.thrd_widget, self.frth_widget]:
            ref_state.extend(el.values)
        ref_state.append(self.total_shafts)
        # check for changes
        if not self.ref or self.ref != ref_state:
            self.ref = ref_state
            redraw = True
        # did a change happen
        if redraw or force:
            #print("Draw SVG, overlays!")
            #print("  plain:",self.plain_state)
            #print("  twill:",self.twill_state)
            #print("  satin:",self.satin_state)
            #
            # rebuild SVG and feedback etc
            self.label = self.create_label()
            ltk.find("#isolabel").val(self.label)
            self.isopattern = ISO_pattern(self.label)
            # calculate svg dimensions
            self.box_dim = int(min(self.dimensions[0]/self.isopattern.grid.width/self.repeats,
                                   self.dimensions[1]/self.isopattern.grid.height/self.repeats,
                                   self.box_min))
            #print(self.box_dim, [self.isopattern.grid.width, self.isopattern.grid.height])
            self.isopattern.grid.build_svg("", repeats=int(self.repeats),
                               dimensions=self.dimensions, box_sq=self.box_dim,
                              box_colors=self.colors)
            ltk.find("#isosvg").html(self.isopattern.grid.diagram.outerHTML)
            ltk.find("#report_area").text(self.isopattern.info())
            # change Weavetype using self.label[0]
            ltk.find("#type_label").text(["Plain","Twill","Satin"][int(self.label[0])-1])
            

def change_shaftcount(event, iso_object):
    """
    UI control affects counts in scnd.
    Called by UI shaft input events.
    """
    #print("Change shaftcount", iso_object)
    # reformat the shafts count UI
    element = ltk.jQuery(event.target)
    value = int(element.val())
    if value < 2:  # minimum
        value = 2
    element.val(f"{value:02d}")
    # check if total adjust invalidates some frth entries
    iso_object.check_alter_frth()
    # adjust any/all values in scnd
    slots = iso_object.scnd_widget.items
    cur_total = sum(int(input.val()) for input in slots)
    count = value - cur_total
    if count > 0:
        # add to input slots
        while count > 0:
            idx = randrange(0, len(slots))
            slots[idx].val(f"{int(slots[idx].val())+1:02d}")
            count -= 1
    elif count < 0:
        # subtract from input slots
        while count < 0:
            idx = randrange(0, len(slots))
            # can't go below "01"
            if sum(int(input.val()) for input in slots) == len(slots):
                # its all '01'
                element.val(f"{len(slots):02d}")
                break
            # if slot has a 1 already - find another
            while int(slots[idx].val()) == 1:
                idx = randrange(0, len(slots))
            slots[idx].val(f"{int(slots[idx].val())-1:02d}")
            count += 1
    # update total
    iso_object.scnd_widget.values = [f"{input.val()}" for input in slots]
    iso_object.total_shafts = sum(int(input.val()) for input in slots)
    iso_object.changed()

def toggle_lock_shafts(event, iso_object):
    """
    Toggle disabling of:
    - shaft input
    - btninc/btndec on scnd UI
    Called by Lock btn.
    """
    # shaftin
    shaftin_el = ltk.find(".shaftbox .shaftin")
    if iso_object.lock_shafts:
        # unlock
        shaftin_el.css("border", "2px solid gray").css("color", "#000")
        shaftin_el.prop("disabled", False)
        iso_object.scnd_widget.enable_buttons()
    else:  # lock
        shaftin_el.css("border", "2px solid #FCC").css("color", "#888")
        shaftin_el.prop("disabled", True)
        iso_object.scnd_widget.disable_buttons()
    iso_object.lock_shafts = not iso_object.lock_shafts

def switch_colors(event, iso_object):
    element = ltk.jQuery(event.target)
    if element.prop('checked'):
        iso_object.colors = ['red','grey']
    else:
        iso_object.colors = ['black','black']
    iso_object.changed(True)

def set_repeats(event, iso_object):
    count = int(ltk.jQuery(event.target).val())
    ltk.jQuery("#repeats").text(f"Repeats {count}:")
    iso_object.repeats = count+1
    iso_object.changed(True)

def save_svg_file(event, iso_object):
    """ Save the svg as a file and send it to the user.
    """
    data = iso_object.isopattern.grid.diagram.outerHTML
    encoded_data = data.encode('utf-8')  # Transform our string of data into bytes
    my_stream = io.BytesIO(encoded_data)  # convert data into bytesIO object
    # Copy of the contents into the JavaScript buffer
    js_array = Uint8Array.new(len(encoded_data))
    js_array.assign(my_stream.getbuffer())
    # File constructor takes a buffer, name, MIME type. (name not used)
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
    file = File.new([js_array], "foo.txt", {type: "image/svg+xml"})  #"text/plain"})
    url = URL.createObjectURL(file)
    hidden_link = ltk.window.document.createElement("a")
    # The second parameter here is the actual name of the file that will appear in the user's file system
    hidden_link.setAttribute("download", f"isoweave - {iso_object.label}.svg")
    hidden_link.setAttribute("href", url)
    hidden_link.click()

def save_wif_file(event, iso_object):
    data = iso_object.isopattern.grid.create_wif("isoweave - "+iso_object.label)
    encoded_data = data.encode('utf-8')  # Transform our string of data into bytes
    my_stream = io.BytesIO(encoded_data)  # convert data into bytesIO object
    # Copy of the contents into the JavaScript buffer
    js_array = Uint8Array.new(len(encoded_data))
    js_array.assign(my_stream.getbuffer())
    # File constructor takes a buffer, name, MIME type. (name not used)
    file = File.new([js_array], "foo.txt", {type: "text/plain"})
    url = URL.createObjectURL(file)
    hidden_link = ltk.window.document.createElement("a")
    # The second parameter here is the actual name of the file that will appear in the user's file system
    hidden_link.setAttribute("download", f"isoweave - {iso_object.label}.wif")
    hidden_link.setAttribute("href", url)
    hidden_link.click()
    
def copy_iso_text(event):
    """
    select the iso text input and copy
    - for user to paste elsewhere
    """
    ltk.jQuery("#isolabel").select()
    ltk.window.document.execCommand("copy")

def create(iso_object):
    """
    Build the main UI control for #isoweaves
    """
    description = "\n".join(["Explore the ISO 9354:1989 specification for basic weave structures.",
                            "The pattern has four sections and defines basic Plain, Twill, and Satin weave structures.",
                            "- Not all variations of these structures are able to be defined by the ISO definition.",
                            "(Source code is located at https://github.com/Neon22/iso-weaves-explorer"])
    report = ltk.VBox(
                ltk.Text("Info:"),
                ltk.TextArea("This is a text area.",
                             {"height": 80 }).attr("id", "report_area")
            )
    UI_controls =  ltk.VBox(
        ltk.HBox(
            ltk.Text("Satin").attr("id", "type_label"),
            ltk.HBox(
                ltk.Input("02").attr("type","number").addClass("shaftin").on("change input", ltk.proxy(lambda event: change_shaftcount(event, iso_object))),
                ltk.Button("Lock", ltk.proxy(lambda event: toggle_lock_shafts(event, iso_object))).addClass("lockbtn")
            ).addClass("shaft_lock_box"),
            ltk.Text("shafts(wefts)").addClass("shaft_label")
        ).addClass("shaftbox"),
        ltk.HBox(
            iso_object.frst_widget,
            ltk.Div("-").addClass("dash"),
            iso_object.scnd_widget,
            ltk.Div("-").addClass("dash"),
            iso_object.thrd_widget,
            ltk.Div("-").addClass("dash"),
            iso_object.frth_widget
        ),
        report
    )
    #
    width,height = iso_object.dimensions
    svg_div = ltk.create(f"""
                <svg id="svg-01" height="{height}" width="{width}">
                    <ellipse id="ellipse" cx="44" cy="44" rx="33" ry="50" style="fill:yellow;stroke:purple;stroke-width:2" />
                </svg>
                """).attr("id","isosvg")
    svg_overlay = ltk.create(f"""
                <svg id="svg-01" height="{height}" width="{width}">
                </svg>
                """).attr("id","svg_overlay")
    iso_textlabel = ltk.HBox(
        ltk.Input("21-01 03-01-01").attr("type","string").attr("id", "isolabel"),  #.attr("disabled",True),
        ltk.Button("Copy text", ltk.proxy(lambda event: copy_iso_text(event))).addClass("copybtn"),
        ltk.Text("Download:").addClass("label2"),
        ltk.Button("SVG", ltk.proxy(lambda event: save_svg_file(event, iso_object))).addClass("copybtn"),
        ltk.Button("WIF", ltk.proxy(lambda event: save_wif_file(event, iso_object))).addClass("copybtn")
    ).addClass("label_box")

    #def animate(event):
    #    UI_controls.animate({ "left": 0, "top": 0 }, 500)

    return (
        ltk.VBox(
            ltk.Heading2("ISO weave - Structure Explorer:"),
            ltk.TextArea(description, {"height": 70 }).attr("id", "description"),
            ltk.HBox(
                ltk.VBox(
                    ltk.HBox(
                    svg_div, svg_overlay).addClass("swatch_box"),
                    # red/blk, repeat counts in here
                    ltk.HBox(
                       ltk.Switch("Red_Grey/Black:", True).addClass("label2").on("change", ltk.proxy(lambda event: switch_colors(event, iso_object))),
                       ltk.Text("Repeats: 1").attr("id","repeats").addClass("label2"),
                       ltk.Input("1").attr("type","range").attr("min","0").attr("max","3").css("width","80px").on("change input", ltk.proxy(lambda event: set_repeats(event, iso_object)))
                    ),
                    iso_textlabel
                    ),
                UI_controls.width(100).draggable()
            ),
            #ltk.HBox(
            #    report
            #)
            #ltk.Text("For clarity, we marked the custom widget orange.")
            #    .css("margin-top", 20),
            #ltk.Heading4("Tip: drag the card and then press the button below"),
            #ltk.Button("Reset", animate).width(90)
        )
        .attr("id", "isoweaves")
    )

def set_iso_pattern(widget, pattern="21-01 03-01-01"):
    """
    Set a start pattern
    """
    parts = [p for p in pattern.split("-")]
    parts[1] = parts[1][0].split()
    for i, part in enumerate(parts):
        self.get_control(i+1).set_values(part)

# Main
if __name__ == "__main__":
    dimensions = [450, 350] # [500,300]
    iso = ISO_widget(dimensions)
    widget = create(iso)
    # only one of these on a page. id = isoweaves
    widget.appendTo(ltk.window.document.body)
    iso.changed()  # signal a refresh to show actual data