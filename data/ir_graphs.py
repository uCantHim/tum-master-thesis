"""Reproduce data mentioned in section "Generating Symbolic Expressions",
Chapter "Implementation".
"""

from miasm.analysis.machine import Machine
from miasm.core.locationdb import LocationDB

from focaccia.arch import x86
from focaccia.miasm_util import MiasmSymbolResolver
from focaccia.snapshot import ProgramState
from focaccia.symbolic import Instruction, run_instruction

def print_ir(instr: Instruction, lifter):
    ircfg = lifter.new_ircfg()
    loc = lifter.add_instr_to_ircfg(instr, ircfg, None, False)

    print('#' * 80)
    print(f'# {instr}')
    print('#')
    print(f'# Entry: {loc}')
    print()
    for block in ircfg.blocks.values():
        print('-' * 25, 'IR block', '-' * 25)
        print(block)
        print('-' * 60)
    print('#' * 80)

def main():
    machine = Machine('x86_64')
    assert(machine.mn is not None)
    loc_db = LocationDB()
    lifter = machine.lifter(loc_db)

    # Generate and print IR blocks for each instruction
    instr = machine.mn.dis(b'\x48\x0f\x45\xd0', 64, 0)  # CMOVNZ RDX, RAX
    print_ir(instr, lifter)
    instr = machine.mn.dis(b'\xf3\xab', 64, 0)          # REP STOSD
    print_ir(instr, lifter)
    print()

    # Generate an assignment form for REP STOSD with a concrete guidance state
    state = ProgramState(x86.ArchX86())
    state.set_register('RCX', 0x10)
    state.set_register('RDX', 0)
    state.set_register('df', 0)
    state.set_register('RAX', 0x42)

    print(instr)
    _, symbs = run_instruction(instr, MiasmSymbolResolver(state, loc_db), lifter)
    for k, v in symbs.items():
        print(f'{str(k):15s} = {v}')

if __name__ == '__main__':
    main()
