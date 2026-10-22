-- Party slot 0 can't lose: HP pinned at max every frame, the six stat bytes set to 99 (one hit kills, before a weakened
-- enemy runs away). The tour's winning battles (scenes.py god=True).
--   emu.py ... --var PARTY=0x800E0918 --script tools/lua/godmode.lua   (slot: max HP +0x0E, HP +0x12, stats +0x18..0x1D)
local ffi = require('ffi')
local base = (PARTY or 0x800E0918) - 0x80000000
L.on_frame(function()
  local p = PCSX.getMemPtr()
  local m = ffi.cast('uint16_t*', p)
  m[(base + 0x12) / 2] = m[(base + 0x0E) / 2]
  for k = 0x18, 0x1D do p[base + k] = 99 end
end)
