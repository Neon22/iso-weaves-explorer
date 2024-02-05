import ltk
from random import randrange
import svg as SVG

# For debugging
def print(*args):
    ltk.find("body").append(" ".join(str(a) for a in args), "<br>")

# Todo:
# - 

highlight_color = "#60CFFF"

def make_svg_overlay(dimensions, rect=[10,10,20,20]):
    style = {"fill":"none", "stroke": highlight_color, "stroke-width": "3px"}
    result = SVG.svg(width=dimensions[0], height=dimensions[1],
                     preserveAspectRatio="xMidYMid meet",
                     viewBox="0 0 {} {}".format(dimensions[0], dimensions[1]))
    if rect:
        box = SVG.rect(x=rect[0], y=rect[1],
                       width=rect[2], height=rect[3],
                       style=style)
        result.appendChild(box)
    return result

class ISO_control_widget(ltk.VBox):
    """
    Vertical stack controlling the values
    in one of the four ISO sections.
    """
    classes = ["control"]
    part1_seq = [10,11,20,21,30,31]
    labels = ["Type","Interlacing","Step","Rise"]
    
    def __init__(self, iso_object, idx, initial_values=[1]):
        """
        Creates the widget
        """
        self.iso_object = iso_object
        self.id = "control-%d" % (idx)
        self.values = []
        self.items = []
        self.draw_highlight = False  # triggered by mouseenter/out events
        #
        self.button_dec = ltk.Button("-", lambda event: self.btndec(event))
        self.button_inc = ltk.Button("+", lambda event: self.btninc(event))
        for b in [self.button_dec, self.button_inc]:
            b.addClass("incdecbtn")
            b.css("text-align", "center")
        if idx == 1:
            btnpair = ltk.HBox(ltk.Div("Spacer").css('visibility', 'hidden'))
        else:
             btnpair = ltk.HBox(self.button_dec,
                                self.button_inc).addClass("btnpair")
        #
        for i,val in enumerate(initial_values):
            value = f"{val:02d}"
            myid = f"{self.id}_{i}"
            item = ltk.Input(value).attr("type","number").attr("id", myid).on("change input", ltk.proxy(lambda event: self.fix_field(event))).on("mouseenter", ltk.proxy(lambda event: self.update_overlay(event, True))).on("mouseout", ltk.proxy(lambda event: self.update_overlay(event, False)))
            self.items.append(item)
            self.values.append(value)
        inputs = ltk.HBox(self.items)
        inputs.addClass("inputs")
        #
        self.button_rnd = ltk.Button("Rnd", lambda event: self.randomcontrol(event)).addClass("rndbtn")
        ltk.VBox.__init__(self,
            btnpair,
            inputs,
            self.button_rnd,
            ltk.Text(self.labels[idx-1]).addClass("modelabel")
        )
        self.attr("id", self.id)
        

    def disable_buttons(self, rand=False):
        self.button_dec.prop("disabled", True)
        self.button_inc.prop("disabled", True)
        if rand:
            self.button_rnd.prop("disabled", True)
            self.items[0].prop("disabled", True)

    def enable_buttons(self, rand=False):
        self.button_dec.prop("disabled", False)
        self.button_inc.prop("disabled", False)
        if rand:
            self.button_rnd.prop("disabled", False)
            self.items[0].prop("disabled", False)

    def update_overlay(self, event, on_off):
        idx = int(self.id[-1])  # which iso_part
        slot = int(ltk.jQuery(event.target).attr("id")[-1])  # which input in that part
        if not self.draw_highlight and on_off:
            self.highlight_on(idx, slot)
            self.draw_highlight = True
        elif self.draw_highlight and not on_off:  # turn it off
            self.highlight_off(idx)
            self.draw_highlight = False

    def highlight_off(self, idx):
        # undraw highlight
        #print(f" {idx} highlight off")
        if idx == 1:  # highlight type name
            ltk.jQuery("#type_label").css("background-color", "#F4F1E2")
        # always undraw the hilight box
        newsvg = make_svg_overlay(self.iso_object.dimensions, None)
        ltk.find("#svg_overlay").html(newsvg.outerHTML)

    def highlight_on(self, idx, slot):
        """
        Draw overlay suitable for each iso_part.
        - triggered when mouse enters/exits input widgets
        """
        box_dim = self.iso_object.box_dim  # calculated box size
        # draw highlight
        #print(f" {idx} highlight on. box: {box_dim}")
        if idx == 1:
            ltk.jQuery("#type_label").css("background-color", highlight_color).css("transition", "background-color ease 0.4s")
            ystart = box_dim * int(self.iso_object.repeats) * self.iso_object.total_shafts -box_dim
            boxdim = [0, ystart, box_dim, box_dim]
        elif idx == 2:
            #slot = int(ltk.jQuery(event.target).attr("id")[-1])
            ymax = box_dim * int(self.iso_object.repeats) * self.iso_object.total_shafts
            ystart = ymax - box_dim * sum([int(val) for val in self.iso_object.scnd_widget.values[:slot+1]])
            yheight = box_dim * int(self.iso_object.scnd_widget.values[slot])
            boxdim = [0, ystart, box_dim, yheight]
            #print(ystart,yheight,ymax)
            #print("",sum([int(val) for val in self.iso_object.scnd_widget.values[:slot+1]]))
        elif idx == 3:
            if len(self.iso_object.thrd_widget.values) == 1:  # only 1 value
                xstart = box_dim * int(self.iso_object.thrd_widget.values[0])
            else:  # several values so highlight actual
                xstart = box_dim * sum([int(val) for val in self.iso_object.thrd_widget.values[:slot]])
            width = box_dim * int(self.iso_object.thrd_widget.values[slot])
            yheight = box_dim * int(self.iso_object.repeats) * self.iso_object.total_shafts
            boxdim = [xstart, 0, width, yheight]
        else:  # idx == 4
            if len(self.iso_object.frth_widget.values) == 1:
                xstart = box_dim * int(self.iso_object.thrd_widget.values[0])
                width = box_dim * int(self.iso_object.thrd_widget.values[0])
                ymax = box_dim * int(self.iso_object.repeats) * self.iso_object.total_shafts
                ystart = ymax - box_dim * int(self.iso_object.frth_widget.values[0])
            else:  # several frth values
                xstart = box_dim * int(self.iso_object.thrd_widget.values[0]) * (slot+1)
                width = box_dim * int(self.iso_object.thrd_widget.values[0])
                #ymax = box_dim * int(self.iso_object.repeats) * self.iso_object.total_shafts
                ymax = box_dim * int(self.iso_object.repeats) * self.iso_object.total_shafts  - box_dim * sum([int(val) for val in self.iso_object.frth_widget.values[:slot]])
                ystart = ymax - box_dim * int(self.iso_object.frth_widget.values[slot])
                #ystart = ymax - box_dim * sum([int(val) for val in self.iso_object.frth_widget.values[:slot+1]])
                #print(int(self.iso_object.repeats) * self.iso_object.total_shafts - sum([int(val) for val in self.iso_object.frth_widget.values[:slot]]))
            boxdim = [xstart, ystart, width, ymax-ystart]
        #
        newsvg = make_svg_overlay(self.iso_object.dimensions, boxdim)
        ltk.find("#svg_overlay").html(newsvg.outerHTML)
    
    def set_values(self, newvalues=["1"]):
        """
        set number/values of items to match values
        - newvalues can be strings from state or numbers
        """
        newnumbers = [int(i) for i in newvalues]
        count = len(self.values) - len(newnumbers)
        group = self.find(".inputs")
        #print("set_values:",newnumbers, self.values, count)
        # correct number of input widgets required
        while count > 0:
            # remove some
            self.values.pop()
            self.items.pop()
            group.children().last().remove()
            #print("pop:",self.values, self.items)
            count -= 1
        if count < 0:
            # add some
            for i in range(abs(count)):
                self.btninc(True)
                #print("Added btinc")
        # set values in those widgets
        #print("-", count, self.values, self.items)
        for i, item in enumerate(self.items):
            value_f = f"{newnumbers[i]:02d}"
            item.val(value_f)
            self.values[i] = value_f
            
    def btninc(self, event):
        """
        Add more inputs to the Control()
        """
        p_id = self.id
        iso_part = int(p_id[-1])
        group = self.find(".inputs")
        # Validate
        count = 1
        # adjust iso_object
        if iso_part == 2:  # scnd - has to be in multiples of 2
            count = 2
        # Adjust UI
        child_count = len(self.values)
        for i in range(count):
            new_id = p_id + "_" + str(child_count + i)
            new_input = ltk.Input("01").attr("type","number").attr("id",new_id).on("change input", ltk.proxy(lambda event: self.fix_field(event))).on("mouseenter", ltk.proxy(lambda event: self.update_overlay(event, True))).on("mouseout", ltk.proxy(lambda event: self.update_overlay(event, False)))
            new_input.appendTo(group)
            self.items.append(new_input)
            self.values.append("01")
            if iso_part == 2:
                self.iso_object.total_shafts += 1
            #print(f"-Adding to iso part: {iso_part} {i} {new_id}")
        self.iso_object.update_UI_shaft_count()
        self.structure_changed()

    def btndec(self, event):
        """
        Decrement the number of inputs in a control
        by deleting the last one (or two)
        """
        group = self.find(".inputs")
        iso_part = int(self.id[-1])
        children = group.children()
        if len(children) > 1:
        #if len(self.values) > 1:
            # Validate
            count = 1
            # adjust iso_object
            if iso_part == 2:  # scnd - has to be in multiples of 2
                count = 2
                if len(children) == 2:
                #if len(self.values) == 2:
                    count = 0  # don't remove last two
                for i in range(count):
                    val = int(self.values.pop())
                    self.items.pop()
                    self.iso_object.total_shafts -= val
                self.iso_object.update_UI_shaft_count()
            elif iso_part == 3 and len(self.values) > 2 and len(self.values)%2 == 0 :
                # thrd has an even number (>2) so pop 2
                for i in range(2):
                    self.values.pop()
                    self.items.pop()
                    count = 2
            else:  # all other parts
                self.values.pop()
                self.items.pop()
            # adjust UI
            for i in range(count):
                group.children().last().remove()
                #print("-Subtracting from iso part:", iso_part)
            if count != 0:
                self.structure_changed()
    
    def randomcontrol(self, event):
        """
        Change values of all inputs in this control
        """
        iso_part = int(self.id[-1])  # grab numeric off end
        #print("Random:In box",iso_part)
        inputs = self.items
        if iso_part == 1:  # frst
            self.iso_object.save_state()  # record for swaps
            current = inputs[0].val()
            guess = [10,11,20,21,30,31][randrange(6)]
            while int(current) == guess:
                # make sure its not the same value
                guess = [10,11,20,21,30,31][randrange(6)]
            value_f = f"{guess:02d}"
            self.values[0] = value_f
            inputs[0].val(value_f)
            if current[0] != value_f[0]:
                # need to change states
                self.update_frst_fields(current[0], value_f[0])
        elif iso_part == 3:
            # if plain then do they have to sum to weftcount
            # if twill,satin then 3 is a single only
            for i, input in enumerate(inputs):
                current = input.val()
                newvalue = randrange(1,4)
                # make sure its not the same value
                while int(current) == newvalue:
                    newvalue = randrange(1,4)
                value_f = f"{newvalue:02d}"
                self.values[i] = value_f
                self.items[i].val(value_f)
        elif iso_part == 4:
            # if satin then 4 is in range [1, total_shafts]
            for i, input in enumerate(inputs):
                current = input.val()
                newvalue = randrange(1, self.iso_object.total_shafts)
                # make sure its not the same value
                while int(current) == newvalue:
                    newvalue = randrange(1, self.iso_object.total_shafts)
                value_f = f"{newvalue:02d}"
                self.values[i] = value_f
                self.items[i].val(value_f)
        else:  # scnd
            count = len(self.values)
            current = [int(i) for i in self.values]
            numbers = []
            if self.iso_object.lock_shafts:
                # locked so randoms must sum to .total_shafts
                total = self.iso_object.total_shafts
                for i in range(count-1):
                    numbers.append(randrange(1,max(2,total+i-count+2-sum(numbers))))
                numbers.append(total-sum(numbers))
            else:  # unlocked
                # get a different set of random numbers to existing
                numbers = [randrange(1,5) for i in range(count)]
                while current == numbers:
                    numbers = [randrange(1,5) for i in range(count)]
                self.iso_object.total_shafts = sum(numbers)
            #
            self.iso_object.update_UI_shaft_count()
            for i in range(len(self.items)):
                value_f = f"{numbers[i]:02d}"
                self.values[i] = value_f
                self.items[i].val(value_f)
        #
        self.structure_changed()

    def fix_field(self, event):
        """
        Validate input events:
        - double digit formatting fix
        - validate frst,scnd,thrd,frth
        - scnd:
          - see if locked. adjust local, then check if totals need fixing
          - adjust others in alter_shafts()
          - set this slot with result of alter_shafts()
        - frst:
          - disable some fields. correct for satins/twills
        - thrd:
          - if plain - any number of non-zero entries
          - if twill - single entry - usually 01 (modulo)
          - if satin - single entry - usually 01 (modulo)
        - frth:
          - if plain - always 00
          - if satin/twill - any number of numbers modulo scnd_size
                           - if 1 number then repeat until sq
        """
        iso_part = int(self.id[-1])  # slot 1 through 4
        element = ltk.jQuery(event.target)
        slot = int(element.attr("id").split("_")[-1])
        oldvalue = int(self.values[slot])
        #print(f"fix_field() isopart: {iso_part} UI,old: {element.val()} {oldvalue} in: {slot}")
        if element.val() == oldvalue:
            # no change required
            pass
            #print(f"..skipping: fix_field() {oldvalue})
        else:
            newvalue = int(element.val())
            #print(f"In: {iso_part} {self.values} {newvalue}")
            if iso_part == 1:
                #print("frst:",oldvalue,newvalue)
                if self.draw_highlight:
                    self.highlight_off(2)
                if newvalue != oldvalue:  # reject the double update
                    self.iso_object.save_state()  # record for swaps
                    if newvalue > oldvalue:  # going up
                        idx = (self.part1_seq.index(oldvalue)+1) % len(self.part1_seq)
                    else:  # going down
                        idx = (self.part1_seq.index(oldvalue)-1) % len(self.part1_seq)
                    value = self.part1_seq[idx]
                    value_f = f"{value:02d}"
                    element.val(value_f)
                    self.values[slot] = value_f
                    if value_f[0] != str(oldvalue)[0]:
                        # changed from plain/twill/satin
                        self.update_frst_fields(str(oldvalue)[0], value_f[0])
                if self.draw_highlight:
                    # highlight being drawn but now in wrong place
                    self.highlight_on(1, int(element.attr("id")[-1]))
            elif iso_part == 2:  # scnd
                if self.draw_highlight:
                    self.highlight_off(2)
                # lock check the shaft count
                value = self.iso_object.alter_shafts(slot, oldvalue, newvalue)
                value_f = f"{value:02d}"
                # update iso_object - proper id field
                element.val(value_f)
                self.iso_object.total_shafts = sum(int(i) for i in self.values)
                # highlight
                if self.draw_highlight:
                    # highlight being drawn but now in wrong place
                    self.highlight_on(2, int(element.attr("id")[-1]))
            elif iso_part == 3:  # thrd
                if self.draw_highlight:
                    self.highlight_off(3)
                if newvalue < 1:  # force no going below 1
                    newvalue = 1
                value_f = f"{newvalue:02d}"
                element.val(value_f)
                self.values[slot] = value_f
                if self.draw_highlight:
                    # highlight being drawn but now in wrong place
                    self.highlight_on(3, int(element.attr("id")[-1]))
            else:  # frth
                if self.draw_highlight:
                    self.highlight_off(4)
                # can't go below 0 or above total_shafts-1
                total = self.iso_object.total_shafts
                if newvalue < 1:  # force no going below 0
                    newvalue = total - 1
                elif newvalue >= total:
                    newvalue = 1
                value_f = f"{newvalue:02d}"
                element.val(value_f)
                self.values[slot] = value_f
                #print(f"  -fixing {element.val()} in {slot}")
                if self.draw_highlight:
                    # highlight being drawn but now in wrong place
                    self.highlight_on(4, int(element.attr("id")[-1]))
            self.structure_changed()

    def update_frst_fields(self, oldvalue, newvalue):
        """
        State has been recorded.
        Restore whole state for twill/satin if disable=False 20,21, and 30,31
        - for Plain: disable frth, set to 0 else 1
        - for Twill,Satin: single thrd
        (Should only be called if oldvalue != newvalue)
        """
        #print("mode was,is:",oldvalue, newvalue)
        if newvalue == '1':  # Plain weave
            if self.iso_object.plain_state:
                thrd,frth = self.iso_object.plain_state
                self.iso_object.thrd_widget.set_values(thrd)
                self.iso_object.frth_widget.set_values(frth)
            else:  # no state recorded yet - play safe
                self.iso_object.frth_widget.set_values(["00"])  # set val to 0
            self.iso_object.disable_part(4, True)
            self.iso_object.enable_part(3, False)
        elif newvalue == '2':  # Twill
            # get twill vals
            if self.iso_object.twill_state:
                thrd,frth = self.iso_object.twill_state
                self.iso_object.thrd_widget.set_values(thrd)
                self.iso_object.frth_widget.set_values(frth)
            else:  # no state recorded yet - play safe
                self.iso_object.thrd_widget.set_values(["01"])
                self.iso_object.frth_widget.set_values(["01"])
            self.iso_object.disable_part(3, False)
            self.iso_object.enable_part(4, True)
        else:  # satin
            self.iso_object.enable_part(4, True)
            # get satin state
            if self.iso_object.satin_state:
                thrd,frth = self.iso_object.satin_state
                self.iso_object.thrd_widget.set_values(thrd)
                self.iso_object.frth_widget.set_values(frth)
            else:  # no state recorded yet - play safe
                self.iso_object.thrd_widget.set_values(["01"])
                self.iso_object.frth_widget.set_values(["01"])
            self.iso_object.disable_part(3, False)
            self.iso_object.enable_part(4, True)


    def structure_changed(self):
        """
        Propogate change up tp top level so
        UI changes to Control() can affect higher levels.
        """
        print("...Replace with your function in subclass.")

# Todo:
# - 

# Ref jquery:
# parent = ltk.jQuery(event.target).parent().parent() # self
# p_id = parent.attr("id")
# group = parent.find(".inputs")
# while int(inputs.first().val()) == guess:
# inputs.each(lambda index, element:
#    ltk.jQuery(element).val(f"{randrange(1,4):02d}"))
#