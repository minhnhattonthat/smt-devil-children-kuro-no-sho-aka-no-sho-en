-- Run the event VM (B_MAIN 0x800262F4) from the field: either an existing script (PTR = RAM address in the overlay) or
-- a synthetic one (OPS = list of bytes, 0x7E end appended). Needs hijack.lua; combine with scene.lua for shots/keys.
--   --var PTR=0x8018971C        --var "OPS={0x15,0,0,0,0x14,0,0x06,0x0C,0x16,0,0,0}"
local SCRIPT = 0x8014F100
L.on_frame(function(n)
  if n ~= 15 then return end
  local ptr = PTR
  if not ptr then
    local m, o = PCSX.getMemPtr(), SCRIPT - 0x80000000
    for k, b in ipairs(OPS) do m[o + k - 1] = b end
    m[o + #OPS] = 0x7E
    ptr = SCRIPT
  end
  H.call(VM or 0x800262F4, ptr)
  L.log(string.format('vm: %08X', ptr))
end)
