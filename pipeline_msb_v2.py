import copy
import sys
from pprint import pprint

# 
# DEFINE MAIN MEMORY and REGS.
# Use as Globals throughout.
# 


def make_reg():
	# Make Global Reg function
	Regs = [0] * 32
	Regs[0] = 0
	for x in range(1, 32):
		Regs[x] = 0x100 + x
	return Regs


def make_mem():
	# Make Global MEM function
	array = range(0, 0xff + 0x1)
	lol_main_memory = []
	for i in range(8):
		lol_main_memory.append(array)
	main_memory = sum(lol_main_memory, [])
	return main_memory


def print_Main_Mem(Main_Mem):
	# print function for MEM
	print "<MAIN MEM>"
	for k, v in enumerate(Main_Mem):
		print Main_Mem[k], ": ", hex(v)


def print_Regs(Regs):
	# print function for REGS
	print "<REG LIST>"
	for k, v in enumerate(Regs):
		print "$", k, ":", hex(v), "\t",


#  define globals so that classes can write them after identifying them as globals
global Regs 
global Main_Mem
Regs = make_reg()
Main_Mem = make_mem()

#
# Pipeline classes
#


class IF_ID():

	def __init__(self, instruction, pc_count):
		self.pc_count = pc_count
		self.instruction = instruction

	def print_vars(self):
		print "______________IF_ID_______________"
		print "Instruction: ", hex(self.instruction)


class ID_EX():

	def __init__(self):
		self.instruction = 0
		self.opcode = 0
		self.reg_dest = 0
		self.alu_src = 0
		self.alu_op = 0
		self.mem_read = 0
		self.mem_write = 0
		self.branch = 0
		self.mem_to_reg = 0
		self.reg_write = 0
		self.seo_offset = 0
		self.incrPC = 0
		self.read_reg_one_val = 0
		self.read_reg_two_val = 0
		self.write_reg_op = 0
		self.write_reg_fun = 0
		self.offset = 0
		self.func = 0
		self.dest = 0
		self.src1 = 0
		self.src2 = 0


# just in case we need to take two compliment.
	def twos_comp(self, val):
		if val >> 15 == 1:
				val -= 2**16
		return val
	# 
	# Parse bit functions
	# Used in calls when deciding on R or I format
	#  

	def parse_func(self, instruction):
			return instruction & 0x3F

	def parse_offset(self, instruction):
			return instruction & 0xFFFF

	def parse_src1(self, instruction):
			return instruction & 0x3E00000

	def parse_src2_dest(self, instruction):
			return instruction & 0x1F0000

	def parse_dest(self, instruction):
			return instruction & 0xF800

	def parse_opcode(self, instruction):
			return instruction & 0xFC000000

	# aggregator function for running cycle

	def ID_EX_run(self, instruction):
		self.instruction = instruction
		self.get_opcode(instruction)
		self.is_I_or_R_format()
		self.when_R_do()
		self.when_I_do()

	def get_opcode(self, instruction):
		self.opcode = self.parse_opcode(self.instruction) >> 26

	def is_I_or_R_format(self):
		# check if instruction is in R format then parse
		# instruction according to R format's schema
		if self.opcode == 0:
			self.func = self.parse_func(self.instruction)
			self.dest = self.parse_dest(self.instruction)
			self.src2 = self.parse_src2_dest(self.instruction)
			self.src1 = self.parse_src1(self.instruction)

		# check if instruction is in I format then parse
		# instruction according to I format's schema
		elif self.opcode != 0:
			self.offset = self.parse_offset(self.instruction)
			self.dest = self.parse_src2_dest(self.instruction)
			self.src1 = self.parse_src1(self.instruction)

		# for debug -- delete later
		# else:
		# 	print "Bug1"

	def when_R_do(self):
		if self.opcode == 0:
			if self.func == 32 or self.func == 34:
				if self.func == 32:
					self.func = 0x20
				if self.func == 34:
					self.func = 0x22

				self.reg_dest = 1
				self.reg_write = 1
				self.alu_op = 0b10
				self.write_reg_op = str(self.src2 >> 16)
				self.write_reg_fun = str(self.dest >> 11)
				self.read_reg_one_val = Regs[self.src1 >> 21]
				self.read_reg_two_val = Regs[self.src2 >> 16]
				self.seo_offset = "NA"  # garbage

		# else:
		# 	print "This is not an R format!"

	def when_I_do(self):
		if self.opcode != 0:

			if self.opcode == 32:
				self.alu_src = 1
				self.mem_to_reg = 1
				self.reg_write = 1
				self.mem_read = 1
				self.alu_op = 0b00
				self.write_reg_op = str(self.dest >> 16)
				self.read_reg_one_val = Regs[self.src1 >> 21]
				self.read_reg_two_val = Regs[self.dest >> 16]
				self.func = "NA"  # garbage
				self.seo_offset = self.twos_comp(self.offset)

			if self.opcode == 40:
				self.reg_dest = "NA"  # garbage
				self.alu_src = 1
				self.mem_to_reg = "NA"  # garbage
				self.mem_write = 1
				self.alu_op = 0b00
				self.func = "NA"  # garbage
				self.write_reg_op = str(self.dest >> 16)
				self.read_reg_one_val = Regs[self.src1 >> 21]
				self.read_reg_two_val = Regs[self.dest >> 16]
				self.seo_offset = self.twos_comp(self.offset)

		# else:
		# 	print "This is not an I format!"
	def print_vars(self):
		print "______________ID_EX________________"
		print "#CONTROL: reg_dest:", self.reg_dest, "alu_src:", self.alu_src, "alu_op:", self.alu_op, "mem_read:", self.mem_read, "mem_write:", self.mem_write, "mem_to_reg:", self.mem_to_reg, "reg_write:", self.reg_write
		print "read_reg_one_val:", hex(self.read_reg_one_val)
		print "read_reg_two_val:", hex(self.read_reg_two_val)
		print "seo_offset:", hex(self.offset)
		print "write_reg_fun:", self.write_reg_fun
		print "write_reg_op:", self.write_reg_op
		print "function:" , self.func

	def reset_props(self):
		dic = vars(self)
		for i in dic.keys():
			if i != '':
				dic[i] = 0


class EX_MEM():

	def __init__(self):

		self.mem_read = 0
		self.mem_write = 0
		self.branch = 0
		self.mem_to_reg = 0
		self.reg_write = 0
		self.read_reg_one_val = 0
		self.read_reg_two_val = 0
		self.seo_offset = 0
		self.alu_op = 0
		self.incrPC = 0
		self.alu_result = 0
		self.store_word_val = 0
		self.write_reg_num = 0

		# this is verbose.  I had this class initiating with all of this, but it didn't work because I have to initiate blank classes at the beginning of my programe for my MAIN(): function to work.
	def assign_values(self, mem_read, mem_write, branch, reg_write, alu_op, read_reg_one_val, read_reg_two_val, seo_offset, func, IncrPC, opcode, reg_dest, write_reg_op, write_reg_fun, mem_to_reg, incrPC):
		self.mem_read = mem_read
		self.mem_write = mem_write
		self.mem_to_reg = mem_to_reg
		self.reg_write = reg_write
		self.branch = branch
		self.incrPC = incrPC
		self.write_reg_num = self.decide_reg_dest(reg_dest, write_reg_fun, write_reg_op)
		self.decide_alu_op(func, alu_op, opcode, read_reg_one_val, read_reg_two_val, seo_offset)

	def decide_reg_dest(self, reg_dest, write_reg_fun, write_reg_op):
		if reg_dest == 1:
			return write_reg_fun
		elif reg_dest == 0:
			return write_reg_op
		else:
			return "NA"

	def decide_alu_op(self, func, alu_op, opcode, read_reg_one_val, read_reg_two_val, seo_offset):
		if alu_op == 0b10:  # R Instruction
				if func == 32:  # add
						self.alu_result = read_reg_one_val + read_reg_two_val
						self.store_word_val = read_reg_two_val
				elif func == 34:  # sub
						self.alu_result = read_reg_one_val - read_reg_two_val
						self.store_word_val = read_reg_two_val

		if alu_op == 0b00:  # I instruction
				if opcode == 0x20:  # lb
						self.alu_result = read_reg_one_val + seo_offset
						self.store_word_val = read_reg_two_val
				elif opcode == 0x28:  # sb
						self.alu_result = read_reg_one_val + seo_offset
						self.store_word_val = read_reg_two_val

	def print_vars(self):
		print "______________EX_MEM________________"
		print "#CONTROL:", "mem_read:", self.mem_read, "mem_write:", self.mem_write, "mem_to_reg:", self.mem_to_reg, "reg_write:", self.reg_write
		print "alu_result:", hex(self.alu_result)
		print "store_word_val:", hex(self.store_word_val)
		print "write_reg_num:", self.write_reg_num

	def reset_props(self):
		dic = vars(self)
		for i in dic.keys():
			if i != '':
				dic[i] = 0


class MEM_WB(object):
	def __init__(self):
		self.mem_to_reg = 0
		self.reg_write = 0
		self.mem_read = 0
		self.mem_write = 0
		self.branch = 0
		self.reg_write = 0
		self.load_value = 0
		self.store_value = 0
		self.alu_result = 0
		self.write_reg_num = 0

		# this is verbose.  I had this class initiating with all of this, but it didn't work because I have to initiate blank classes at the beginning of my programe for my MAIN(): function to work.
	def to_mem(self, mem_to_reg, reg_write, alu_result, write_reg_num, mem_read, store_word_val, mem_write):
		self.mem_to_reg = mem_to_reg
		self.reg_write = reg_write
		self.alu_result = alu_result
		self.write_reg_num = write_reg_num
		self.store_value = store_word_val
		self.mem_read_write(mem_read, mem_write, alu_result, store_word_val)
		self.write_back()

	def mem_read_write(self, mem_read, mem_write, alu_result, store_word_val):
		if mem_read == 1:  # load
			self.load_value = Main_Mem[alu_result]

		if mem_write == 1:  # store
			Main_Mem[alu_result] = store_word_val

	def write_back(self):

		global Regs

		if self.write_reg_num != "NA":
				if self.mem_write == 0 and self.mem_to_reg == 0:  # r
						Regs[int(self.write_reg_num)] = self.alu_result

				elif self.mem_write == 0 and self.mem_to_reg == 1:  # lw
						self.load_value = Main_Mem[self.alu_result]
						Regs[int(self.write_reg_num)] = self.load_value

	def print_vars(self):
		print "______________MEM_WB________________"
		print "#CONTROL:", "mem_to_reg:", self.mem_to_reg, "reg_write:", self.reg_write
		print "alu_result:", hex(self.alu_result)
		print "store_word_val:", hex(self.store_value)
		print "write_reg_num", self.write_reg_num

	def reset_props(self):
		dic = vars(self)
		for i in dic.keys():
			if i != '':
				dic[i] = 0

#  !------ start triggers --------!
# 	in functions to the objects can be transient. 
# 	Won't have to worry about flushing an object everytime
# 	Always copy from a read, never a write otherwise we skip a step.


def IF_Stage(instruction, address):

	# initialize IF_stage object
	IF_write.instruction = instruction
	IF_write.address = address


def ID_Stage():
	ID_write.ID_EX_run(IF_read.instruction)


def EX_Stage():
	EX_write.assign_values(ID_read.mem_read, ID_read.mem_write, ID_read.branch, ID_read.reg_write, ID_read.alu_op, ID_read.read_reg_one_val, ID_read.read_reg_two_val, ID_read.seo_offset, ID_read.func, ID_read.incrPC, ID_read.opcode, ID_read.reg_dest, ID_read.write_reg_op, ID_read.write_reg_fun, ID_read.mem_to_reg, ID_read.incrPC)


def MEM_Stage():
	MEM_write.to_mem(EX_read.mem_to_reg, EX_read.reg_write, EX_read.alu_result, EX_read.write_reg_num, EX_read.mem_read, EX_read.store_word_val, EX_read.mem_write)


def WB_Stage():
	MEM_write.write_back()


#  print out all of class print methods


def Print_out_everything():
	IF_write.print_vars()
	print "--Write--"
	IF_read.print_vars()
	print "--Read--"
	ID_write.print_vars()
	print "--Write--"
	ID_read.print_vars()
	print "--Read--"
	EX_write.print_vars()
	print "--Write--"
	EX_read.print_vars()
	print "--Read--"
	MEM_write.print_vars()
	print "--Write--"
	MEM_read.print_vars()
	print "--Read--"
	print_Regs(Regs)
	print ""
	print ""

# flush object values for new write

def prop_flush():
	ID_write.reset_props()
	EX_write.reset_props()
	MEM_write.reset_props()


# copy all of the write to read.  Needed to deepcopy so that we create a new object and not just an object that points to the same place in memory.  Have to set the reads to global to reach outside of the function to be used outside of the function scope


def Copy_write_to_read():
	global IF_read
	global ID_read
	global EX_read
	global MEM_read

	IF_read = copy.deepcopy(IF_write)
	ID_read = copy.deepcopy(ID_write)
	EX_read = copy.deepcopy(EX_write)
	MEM_read = copy.deepcopy(MEM_write)

	prop_flush()



instructions = [0xa1020000, 0x810AFFFC, 0x00831820, 0x01263820, 0x01224820, 0x81180000, 0x81510010, 0x00624022, 0x00000000, 0x00000000, 0x00000000, 0x00000000]



def MAIN():

	IF_write = IF_ID(0x0, 0)
	IF_read = IF_ID(0x0, 0x0)

	ID_write = ID_EX()
	ID_read = ID_EX()

	EX_write = EX_MEM()
	EX_read = EX_MEM()

	MEM_write = MEM_WB()
	MEM_read = MEM_WB()

	clock_counter = 0
	current_address = 0x7a000

	print "#################### CLOCK CYCLE", clock_counter, "###########################"
	Print_out_everything()
	print ''


	for i in instructions:
		clock_counter += 1
		print "#################### CLOCK CYCLE", clock_counter, "###########################"

		IF_Stage(i, current_address)
		ID_Stage()
		EX_Stage()
		MEM_Stage()
		Print_out_everything()
		Copy_write_to_read()
		current_address += 4

MAIN()