--[[
================================================================================
DaVinci Resolve MCP - In-App Lua Bridge
================================================================================
Enables Model Context Protocol (MCP) automation for DaVinci Resolve using native Lua!

Why Lua?
- Embedded in EVERY DaVinci Resolve installation (Free & Studio).
- Requires ZERO Python installation, environment variables, or pip packages inside Resolve.
- Guaranteed to appear in Workspace > Scripts on all platforms (macOS, Windows, Linux).

Usage in DaVinci Resolve:
1. Open DaVinci Resolve and load any project.
2. In the top menu bar, click:
     Workspace > Scripts > Utility > davinci_resolve_mcp_bridge
3. A confirmation banner will appear in your Console.
4. Keep DaVinci Resolve open. Your AI assistant (Claude, Cursor, etc.) will connect!
================================================================================
--]]

local BRIDGE_VERSION = "1.0.0"

--------------------------------------------------------------------------------
-- 1. Embedded Pure Lua JSON Library (rxi/json.lua - MIT License)
--------------------------------------------------------------------------------
local json = { _version = "0.1.2" }

local encode
local escape_char_map = {
  [ "\\" ] = "\\", [ "\"" ] = "\"", [ "\b" ] = "b",
  [ "\f" ] = "f",  [ "\n" ] = "n",  [ "\r" ] = "r",  [ "\t" ] = "t",
}
local escape_char_map_inv = { [ "/" ] = "/" }
for k, v in pairs(escape_char_map) do escape_char_map_inv[v] = k end

local function escape_char(c)
  return "\\" .. (escape_char_map[c] or string.format("u%04x", c:byte()))
end

local function encode_nil(val) return "null" end

local function encode_table(val, stack)
  local res = {}
  stack = stack or {}
  if stack[val] then error("circular reference") end
  stack[val] = true

  if rawget(val, 1) ~= nil or next(val) == nil then
    local n = 0
    for k in pairs(val) do
      if type(k) ~= "number" then error("invalid table: mixed or invalid key types") end
      n = n + 1
    end
    if n ~= #val then error("invalid table: sparse array") end
    for i, v in ipairs(val) do
      table.insert(res, encode(v, stack))
    end
    stack[val] = nil
    return "[" .. table.concat(res, ",") .. "]"
  else
    for k, v in pairs(val) do
      if type(k) ~= "string" then error("invalid table: mixed or invalid key types") end
      table.insert(res, encode(k, stack) .. ":" .. encode(v, stack))
    end
    stack[val] = nil
    return "{" .. table.concat(res, ",") .. "}"
  end
end

local function encode_string(val)
  return '"' .. val:gsub('[%z\1-\31\\"]', escape_char) .. '"'
end

local function encode_number(val)
  if val ~= val or val <= -math.huge or val >= math.huge then
    error("unexpected number value '" .. tostring(val) .. "'")
  end
  return string.format("%.14g", val)
end

local type_func_map = {
  [ "nil"     ] = encode_nil,
  [ "table"   ] = encode_table,
  [ "string"  ] = encode_string,
  [ "number"  ] = encode_number,
  [ "boolean" ] = tostring,
}

encode = function(val, stack)
  local t = type(val)
  local f = type_func_map[t]
  if f then return f(val, stack) end
  error("unexpected type '" .. t .. "'")
end

function json.encode(val) return encode(val) end

-- Decode
local function create_set(...)
  local res = {}
  for i = 1, select("#", ...) do res[ select(i, ...) ] = true end
  return res
end

local space_chars  = create_set(" ", "\t", "\r", "\n")
local delim_chars  = create_set(" ", "\t", "\r", "\n", "]", "}", ",")
local escape_chars = create_set("\\", "/", '"', "b", "f", "n", "r", "t", "u")
local literals     = create_set("true", "false", "null")

local literal_map = { [ "true" ] = true, [ "false" ] = false, [ "null" ] = nil }

local function next_char(str, idx, set, negate)
  for i = idx, #str do
    if set[str:sub(i, i)] ~= negate then return i end
  end
  return #str + 1
end

local function decode_error(str, idx, msg)
  local line_count = 1
  local col_count = 1
  for i = 1, idx - 1 do
    col_count = col_count + 1
    if str:sub(i, i) == "\n" then
      line_count = line_count + 1
      col_count = 1
    end
  end
  error(string.format("%s at line %d col %d", msg, line_count, col_count))
end

local function codepoint_to_utf8(n)
  local f = math.floor
  if n <= 0x7f then return string.char(n)
  elseif n <= 0x7ff then return string.char(f(n / 64) + 192, n % 64 + 128)
  elseif n <= 0xffff then return string.char(f(n / 4096) + 224, f(n % 4096 / 64) + 128, n % 64 + 128)
  elseif n <= 0x10ffff then return string.char(f(n / 262144) + 240, f(n % 262144 / 4096) + 128, f(n % 4096 / 64) + 128, n % 64 + 128)
  end
  error(string.format("invalid codepoint '%x'", n))
end

local function parse_unicode_escape(s)
  local n1 = tonumber(s:sub(1, 4), 16)
  local n2 = tonumber(s:sub(7, 10), 16)
  if n2 then return codepoint_to_utf8((n1 - 0xd800) * 0x400 + (n2 - 0xdc00) + 0x10000)
  else return codepoint_to_utf8(n1) end
end

local function parse_string(str, i)
  local res = ""
  local j = i + 1
  local k = j

  while j <= #str do
    local x = str:byte(j)
    if x < 32 then decode_error(str, j, "control character in string")
    elseif x == 92 then
      res = res .. str:sub(k, j - 1)
      j = j + 1
      local c = str:sub(j, j)
      if c == "u" then
        local hex = str:match("^[dD][89aAbB]%x%x\\u%x%x%x%x", j + 1) or str:match("^%x%x%x%x", j + 1)
          or decode_error(str, j - 1, "invalid unicode escape in string")
        res = res .. parse_unicode_escape(hex)
        j = j + #hex
      else
        if not escape_chars[c] then decode_error(str, j - 1, "invalid escape char '" .. c .. "' in string") end
        res = res .. escape_char_map_inv[c]
      end
      k = j + 1
    elseif x == 34 then
      res = res .. str:sub(k, j - 1)
      return res, j + 1
    end
    j = j + 1
  end
  decode_error(str, i, "expected closing quote for string")
end

local function parse_number(str, i)
  local x = next_char(str, i, delim_chars)
  local s = str:sub(i, x - 1)
  local n = tonumber(s)
  if not n then decode_error(str, i, "invalid number '" .. s .. "'") end
  return n, x
end

local function parse_literal(str, i)
  local x = next_char(str, i, delim_chars)
  local word = str:sub(i, x - 1)
  if not literals[word] then decode_error(str, i, "invalid literal '" .. word .. "'") end
  return literal_map[word], x
end

local function parse_array(str, i)
  local res = {}
  local n = 1
  i = i + 1
  while 1 do
    local x
    i = next_char(str, i, space_chars, true)
    if str:sub(i, i) == "]" then i = i + 1 break end
    x, i = json.parse_val(str, i)
    res[n] = x
    n = n + 1
    i = next_char(str, i, space_chars, true)
    local chr = str:sub(i, i)
    i = i + 1
    if chr == "]" then break end
    if chr ~= "," then decode_error(str, i, "expected ']' or ','") end
  end
  return res, i
end

local function parse_object(str, i)
  local res = {}
  i = i + 1
  while 1 do
    local key, val
    i = next_char(str, i, space_chars, true)
    if str:sub(i, i) == "}" then i = i + 1 break end
    if str:sub(i, i) ~= '"' then decode_error(str, i, "expected string for key") end
    key, i = parse_string(str, i)
    i = next_char(str, i, space_chars, true)
    if str:sub(i, i) ~= ":" then decode_error(str, i, "expected ':' after key") end
    i = next_char(str, i + 1, space_chars, true)
    val, i = json.parse_val(str, i)
    res[key] = val
    i = next_char(str, i, space_chars, true)
    local chr = str:sub(i, i)
    i = i + 1
    if chr == "}" then break end
    if chr ~= "," then decode_error(str, i, "expected '}' or ','") end
  end
  return res, i
end

local char_func_map = {
  [ '"' ] = parse_string, [ "0" ] = parse_number, [ "1" ] = parse_number,
  [ "2" ] = parse_number, [ "3" ] = parse_number, [ "4" ] = parse_number,
  [ "5" ] = parse_number, [ "6" ] = parse_number, [ "7" ] = parse_number,
  [ "8" ] = parse_number, [ "9" ] = parse_number, [ "-" ] = parse_number,
  [ "t" ] = parse_literal,[ "f" ] = parse_literal,[ "n" ] = parse_literal,
  [ "[" ] = parse_array,  [ "{" ] = parse_object,
}

json.parse_val = function(str, idx)
  local chr = str:sub(idx, idx)
  local f = char_func_map[chr]
  if f then return f(str, idx) end
  decode_error(str, idx, "unexpected character '" .. chr .. "'")
end

function json.decode(str)
  if type(str) ~= "string" then error("expected argument of type string, got " .. type(str)) end
  local res, idx = json.parse_val(str, next_char(str, 1, space_chars, true))
  idx = next_char(str, idx, space_chars, true)
  if idx <= #str then decode_error(str, idx, "trailing garbage") end
  return res
end

--------------------------------------------------------------------------------
-- 2. DaVinci Resolve Runtime Access
--------------------------------------------------------------------------------
local function get_resolve()
  if resolve ~= nil then return resolve end
  if app ~= nil and app.GetResolve ~= nil then
    local r = app:GetResolve()
    if r ~= nil then return r end
  end
  if bmd ~= nil and bmd.scriptapp ~= nil then
    local r = bmd:scriptapp("Resolve")
    if r ~= nil then return r end
  end
  return nil
end

local dvr = get_resolve()
if not dvr then
  print("[DaVinci Resolve MCP Lua Bridge] ❌ Error: Could not obtain Resolve object.")
  return
end

local pm = dvr:GetProjectManager()

--------------------------------------------------------------------------------
-- 3. File IPC Setup
--------------------------------------------------------------------------------
local function get_ipc_dir()
  local home = os.getenv("HOME") or os.getenv("USERPROFILE") or ""
  local sep = package.config:sub(1, 1) -- '/' on Unix, '\' on Windows
  local dir = home .. sep .. ".davinci_resolve_mcp_ipc"
  -- Create dir if possible
  if sep == "/" then
    os.execute("mkdir -p '" .. dir .. "' 2>/dev/null")
  else
    os.execute('mkdir "' .. dir .. '" 2>nul')
  end
  return dir, sep
end

local ipc_dir, sep = get_ipc_dir()
local req_file = ipc_dir .. sep .. "request.json"
local resp_file = ipc_dir .. sep .. "response.json"
local status_file = ipc_dir .. sep .. "status.json"

local function read_file(path)
  local f = io.open(path, "r")
  if not f then return nil end
  local content = f:read("*a")
  f:close()
  return content
end

local function write_file(path, content)
  local f = io.open(path, "w")
  if not f then return false end
  f:write(content)
  f:close()
  return true
end

local function write_status()
  local proj = pm and pm:GetCurrentProject() or nil
  local tl = proj and proj:GetCurrentTimeline() or nil
  local status_data = {
    connected = true,
    bridge_type = "lua",
    product_name = dvr:GetProductName(),
    version = dvr:GetVersionString(),
    current_project = proj and proj:GetName() or nil,
    current_timeline = tl and tl:GetName() or nil,
    timeline_count = proj and proj:GetTimelineCount() or 0,
    timestamp = os.time(),
  }
  write_file(status_file, json.encode(status_data))
end

--------------------------------------------------------------------------------
-- 4. Native Lua Tool Handlers (49 Tools)
--------------------------------------------------------------------------------
local handlers = {}

-- 1. Project Management
handlers["get_resolve_status"] = function(args)
  local proj = pm:GetCurrentProject()
  local tl = proj and proj:GetCurrentTimeline() or nil
  return {
    connected = true,
    mode = "in_app_lua_bridge",
    product_name = dvr:GetProductName(),
    version = dvr:GetVersionString(),
    current_project = proj and proj:GetName() or nil,
    current_timeline = tl and tl:GetName() or nil,
    timeline_count = proj and proj:GetTimelineCount() or 0,
  }
end

handlers["list_projects"] = function(args)
  local list = pm:GetProjectListInCurrentFolder() or {}
  return { count = #list, projects = list }
end

handlers["open_project"] = function(args)
  local proj = pm:LoadProject(args.project_name)
  if not proj then
    return { success = false, error = "Failed to load project '" .. tostring(args.project_name) .. "'." }
  end
  return { success = true, project_name = proj:GetName(), timeline_count = proj:GetTimelineCount() }
end

handlers["create_project"] = function(args)
  local proj = pm:CreateProject(args.project_name)
  if not proj then
    return { success = false, error = "Failed to create project '" .. tostring(args.project_name) .. "'." }
  end
  return { success = true, project_name = proj:GetName() }
end

handlers["save_project"] = function(args)
  return { success = pm:SaveProject() and true or false }
end

handlers["close_project"] = function(args)
  local proj = pm:GetCurrentProject()
  if not proj then return { success = false, error = "No project currently open." } end
  local name = proj:GetName()
  local ok = pm:CloseProject(proj)
  return { success = ok and true or false, closed_project = name }
end

handlers["get_project_settings"] = function(args)
  local proj = pm:GetCurrentProject()
  if not proj then return { success = false, error = "No project open." } end
  local all = proj:GetSetting() or {}
  local keys = args.keys or { "timelineResolutionWidth", "timelineResolutionHeight", "timelineFrameRate", "timelinePlaybackFrameRate" }
  local res = {}
  for _, k in ipairs(keys) do
    if all[k] ~= nil then res[k] = all[k] end
  end
  return res
end

handlers["set_project_setting"] = function(args)
  local proj = pm:GetCurrentProject()
  if not proj then return { success = false, error = "No project open." } end
  local ok = proj:SetSetting(args.setting_name, tostring(args.value))
  return { success = ok and true or false, setting = args.setting_name, value = args.value }
end

-- 2. Media Pool
handlers["get_media_pool_structure"] = function(args)
  local proj = pm:GetCurrentProject()
  if not proj then return { success = false, error = "No project open." } end
  local mp = proj:GetMediaPool()
  local root = mp:GetRootFolder()
  return {
    root_bin = root:GetName(),
    clip_count = #(root:GetClipList() or {}),
    sub_bin_count = #(root:GetSubFolderList() or {}),
  }
end

handlers["create_bin"] = function(args)
  local proj = pm:GetCurrentProject()
  local mp = proj and proj:GetMediaPool()
  if not mp then return { success = false, error = "No media pool." } end
  local parent = mp:GetRootFolder()
  local bin = mp:AddSubFolder(parent, args.bin_name)
  if not bin then return { success = false, error = "Failed to create bin." } end
  return { success = true, bin_name = bin:GetName() }
end

handlers["import_media"] = function(args)
  local proj = pm:GetCurrentProject()
  local mp = proj and proj:GetMediaPool()
  if not mp then return { success = false, error = "No media pool." } end
  local clips = mp:ImportMedia(args.file_paths or {}) or {}
  local names = {}
  for _, c in ipairs(clips) do table.insert(names, c:GetName()) end
  return { success = #clips > 0, imported_count = #clips, clips = names }
end

handlers["list_media_pool_clips"] = function(args)
  local proj = pm:GetCurrentProject()
  local mp = proj and proj:GetMediaPool()
  if not mp then return { success = false, error = "No media pool." } end
  local root = mp:GetRootFolder()
  local clips = root:GetClipList() or {}
  local res = {}
  for _, c in ipairs(clips) do
    local props = c:GetClipProperty() or {}
    table.insert(res, { name = c:GetName(), duration = props["Duration"], fps = props["FPS"] })
  end
  return { count = #res, clips = res }
end

handlers["create_empty_timeline"] = function(args)
  local proj = pm:GetCurrentProject()
  local mp = proj and proj:GetMediaPool()
  if not mp then return { success = false, error = "No media pool." } end
  local tl = mp:CreateEmptyTimeline(args.timeline_name)
  if not tl then return { success = false, error = "Failed to create empty timeline." } end
  return { success = true, timeline_name = tl:GetName() }
end

handlers["create_timeline_from_clips"] = function(args)
  local proj = pm:GetCurrentProject()
  local mp = proj and proj:GetMediaPool()
  if not mp then return { success = false, error = "No media pool." } end
  local root = mp:GetRootFolder()
  local clips = root:GetClipList() or {}
  local tl = mp:CreateTimelineFromClips(args.timeline_name, clips)
  if not tl then return { success = false, error = "Failed to create timeline from clips." } end
  return { success = true, timeline_name = tl:GetName() }
end

handlers["append_clips_to_timeline"] = function(args)
  local proj = pm:GetCurrentProject()
  local mp = proj and proj:GetMediaPool()
  if not mp then return { success = false, error = "No media pool." } end
  local root = mp:GetRootFolder()
  local clips = root:GetClipList() or {}
  local ok = mp:AppendToTimeline(clips)
  return { success = ok and true or false }
end

-- 3. Timeline & Inspector
handlers["list_timelines"] = function(args)
  local proj = pm:GetCurrentProject()
  if not proj then return { success = false, error = "No project open." } end
  local count = proj:GetTimelineCount() or 0
  local current = proj:GetCurrentTimeline()
  local currentName = current and current:GetName() or nil
  local timelines = {}
  for i = 1, count do
    local tl = proj:GetTimelineByIndex(i)
    if tl then
      table.insert(timelines, { index = i, name = tl:GetName(), is_current = (tl:GetName() == currentName) })
    end
  end
  return { count = #timelines, current_timeline = currentName, timelines = timelines }
end

handlers["set_current_timeline"] = function(args)
  local proj = pm:GetCurrentProject()
  if not proj then return { success = false, error = "No project open." } end
  local count = proj:GetTimelineCount() or 0
  local target = nil
  local ident = args.timeline_name_or_index
  local idx = tonumber(ident)
  if idx and idx >= 1 and idx <= count then
    target = proj:GetTimelineByIndex(idx)
  else
    for i = 1, count do
      local tl = proj:GetTimelineByIndex(i)
      if tl and tl:GetName() == tostring(ident) then target = tl break end
    end
  end
  if not target then return { success = false, error = "Timeline not found." } end
  local ok = proj:SetCurrentTimeline(target)
  return { success = ok and true or false, active_timeline = target:GetName() }
end

handlers["duplicate_timeline"] = function(args)
  local proj = pm:GetCurrentProject()
  local tl = proj and proj:GetCurrentTimeline()
  if not tl then return { success = false, error = "No active timeline." } end
  local newTl = tl:DuplicateTimeline(args.new_name)
  if not newTl then return { success = false, error = "Failed to duplicate timeline." } end
  return { success = true, duplicated_timeline = newTl:GetName() }
end

handlers["get_timeline_info"] = function(args)
  local proj = pm:GetCurrentProject()
  local tl = proj and proj:GetCurrentTimeline()
  if not tl then return { success = false, error = "No active timeline." } end
  return {
    name = tl:GetName(),
    start_frame = tl:GetStartFrame(),
    end_frame = tl:GetEndFrame(),
    start_timecode = tl:GetStartTimecode(),
    track_counts = {
      video = tl:GetTrackCount("video") or 0,
      audio = tl:GetTrackCount("audio") or 0,
      subtitle = tl:GetTrackCount("subtitle") or 0,
    }
  }
end

handlers["get_track_items"] = function(args)
  local proj = pm:GetCurrentProject()
  local tl = proj and proj:GetCurrentTimeline()
  if not tl then return { success = false, error = "No active timeline." } end
  local trackType = string.lower(args.track_type or "video")
  local trackIdx = tonumber(args.track_index or 1)
  local items = tl:GetItemListInTrack(trackType, trackIdx) or {}
  local res = {}
  for idx, item in ipairs(items) do
    local mpItem = item:GetMediaPoolItem()
    table.insert(res, {
      index = idx,
      name = item:GetName(),
      start = item:GetStart(),
      ["end"] = item:GetEnd(),
      duration = item:GetDuration(),
      source_clip = mpItem and mpItem:GetName() or nil
    })
  end
  return { success = true, track_type = trackType, track_index = trackIdx, count = #res, items = res }
end

handlers["get_clip_properties"] = function(args)
  local proj = pm:GetCurrentProject()
  local tl = proj and proj:GetCurrentTimeline()
  if not tl then return { success = false, error = "No active timeline." } end
  local items = tl:GetItemListInTrack(string.lower(args.track_type or "video"), tonumber(args.track_index or 1)) or {}
  local idx = tonumber(args.item_index or 1)
  if idx < 1 or idx > #items then return { success = false, error = "Item index out of range." } end
  local item = items[idx]
  return { success = true, clip_name = item:GetName(), properties = item:GetProperty() or {} }
end

handlers["set_clip_properties"] = function(args)
  local proj = pm:GetCurrentProject()
  local tl = proj and proj:GetCurrentTimeline()
  if not tl then return { success = false, error = "No active timeline." } end
  local items = tl:GetItemListInTrack(string.lower(args.track_type or "video"), tonumber(args.track_index or 1)) or {}
  local idx = tonumber(args.item_index or 1)
  if idx < 1 or idx > #items then return { success = false, error = "Item index out of range." } end
  local item = items[idx]
  local updated = {}
  for k, v in pairs(args.properties or {}) do
    updated[k] = item:SetProperty(k, v) and true or false
  end
  return { success = true, clip_name = item:GetName(), applied = updated }
end

handlers["add_marker"] = function(args)
  local proj = pm:GetCurrentProject()
  local tl = proj and proj:GetCurrentTimeline()
  if not tl then return { success = false, error = "No active timeline." } end
  local frame = tonumber(args.frame_id or 0)
  local color = args.color or "Blue"
  local name = args.name or ""
  local note = args.note or ""
  local duration = tonumber(args.duration or 1)
  local ok = tl:AddMarker(frame, color, name, note, duration)
  return { success = ok and true or false, frame_id = frame, color = color }
end

handlers["get_markers"] = function(args)
  local proj = pm:GetCurrentProject()
  local tl = proj and proj:GetCurrentTimeline()
  if not tl then return { success = false, error = "No active timeline." } end
  local markers = tl:GetMarkers() or {}
  return { success = true, markers = markers }
end

handlers["delete_marker"] = function(args)
  local proj = pm:GetCurrentProject()
  local tl = proj and proj:GetCurrentTimeline()
  if not tl then return { success = false, error = "No active timeline." } end
  if args.frame_id ~= nil then
    local ok = tl:DeleteMarkerAtFrame(tonumber(args.frame_id))
    return { success = ok and true or false, deleted_frame = args.frame_id }
  elseif args.color ~= nil then
    local ok = tl:DeleteMarkersByColor(args.color)
    return { success = ok and true or false, deleted_color = args.color }
  end
  return { success = false, error = "Must provide frame_id or color." }
end

-- 4. Fusion, Titles & Graphics
handlers["insert_generator_into_timeline"] = function(args)
  local proj = pm:GetCurrentProject()
  local mp = proj and proj:GetMediaPool()
  if not mp then return { success = false, error = "No media pool." } end
  local item = mp:InsertGeneratorIntoTimeline(args.generator_name)
  if not item then return { success = false, error = "Failed to insert generator." } end
  return { success = true, generator_name = args.generator_name }
end

handlers["insert_title_into_timeline"] = function(args)
  local proj = pm:GetCurrentProject()
  local mp = proj and proj:GetMediaPool()
  if not mp then return { success = false, error = "No media pool." } end
  local item = mp:InsertTitleIntoTimeline(args.title_name)
  if not item then return { success = false, error = "Failed to insert title." } end
  return { success = true, title_name = args.title_name }
end

handlers["insert_fusion_title_into_timeline"] = function(args)
  local proj = pm:GetCurrentProject()
  local mp = proj and proj:GetMediaPool()
  if not mp then return { success = false, error = "No media pool." } end
  local item = mp:InsertFusionTitleIntoTimeline(args.template_name)
  if not item then return { success = false, error = "Failed to insert Fusion title." } end
  return { success = true, template_name = args.template_name }
end

handlers["set_text_plus_properties"] = function(args)
  local proj = pm:GetCurrentProject()
  local tl = proj and proj:GetCurrentTimeline()
  if not tl then return { success = false, error = "No active timeline." } end
  local items = tl:GetItemListInTrack("video", tonumber(args.track_index or 1)) or {}
  local idx = tonumber(args.item_index or 1)
  if idx < 1 or idx > #items then return { success = false, error = "Item index out of range." } end
  local item = items[idx]
  local comp = item:GetFusionCompByIndex(1)
  if not comp then return { success = false, error = "No Fusion composition found on clip." } end
  local tools = comp:GetToolList() or {}
  for _, tool in pairs(tools) do
    if tool:GetAttrs("TOOLS_RegID") == "TextPlus" then
      if args.text then tool.StyledText = args.text end
      if args.font then tool.Font = args.font end
      if args.size then tool.Size = tonumber(args.size) end
      return { success = true, tool_name = tool:GetAttrs("TOOLS_Name") }
    end
  end
  return { success = false, error = "No Text+ tool found in composition." }
end

handlers["get_fusion_comp_tools"] = function(args)
  local proj = pm:GetCurrentProject()
  local tl = proj and proj:GetCurrentTimeline()
  if not tl then return { success = false, error = "No active timeline." } end
  local items = tl:GetItemListInTrack("video", tonumber(args.track_index or 1)) or {}
  local idx = tonumber(args.item_index or 1)
  if idx < 1 or idx > #items then return { success = false, error = "Item index out of range." } end
  local item = items[idx]
  local comp = item:GetFusionCompByIndex(1)
  if not comp then return { success = false, error = "No Fusion composition." } end
  local tools = comp:GetToolList() or {}
  local res = {}
  for _, tool in pairs(tools) do
    table.insert(res, { name = tool:GetAttrs("TOOLS_Name"), id = tool:GetAttrs("TOOLS_RegID") })
  end
  return { success = true, tool_count = #res, tools = res }
end

-- 5. Audio & Studio-Only Notices
handlers["get_voice_isolation"] = function(args)
  return { success = false, error = "Voice Isolation requires DaVinci Resolve Studio (DaVinci Neural Engine feature)." }
end

handlers["set_voice_isolation"] = function(args)
  return { success = false, error = "Voice Isolation requires DaVinci Resolve Studio (DaVinci Neural Engine feature)." }
end

handlers["create_subtitles_from_audio"] = function(args)
  return { success = false, error = "Auto speech-to-text subtitles requires DaVinci Resolve Studio." }
end

handlers["get_fairlight_presets"] = function(args)
  local presets = dvr:GetFairlightPresets() or {}
  return { success = true, presets = presets }
end

handlers["apply_fairlight_preset"] = function(args)
  local proj = pm:GetCurrentProject()
  if not proj then return { success = false, error = "No project open." } end
  local ok = proj:ApplyFairlightPresetToCurrentTimeline(args.preset_name)
  return { success = ok and true or false, preset_name = args.preset_name }
end

-- 6. Color Grading
handlers["apply_grade_from_drx"] = function(args)
  local proj = pm:GetCurrentProject()
  local tl = proj and proj:GetCurrentTimeline()
  if not tl then return { success = false, error = "No active timeline." } end
  local ok = tl:ApplyGradeFromDRX(args.path, tonumber(args.grade_mode or 0))
  return { success = ok and true or false }
end

handlers["set_clip_lut"] = function(args)
  local proj = pm:GetCurrentProject()
  local tl = proj and proj:GetCurrentTimeline()
  if not tl then return { success = false, error = "No active timeline." } end
  local items = tl:GetItemListInTrack("video", tonumber(args.track_index or 1)) or {}
  local idx = tonumber(args.item_index or 1)
  if idx < 1 or idx > #items then return { success = false, error = "Item index out of range." } end
  local ok = items[idx]:SetLUT(tonumber(args.node_index or 1), args.lut_path)
  return { success = ok and true or false }
end

handlers["set_clip_cdl"] = function(args)
  local proj = pm:GetCurrentProject()
  local tl = proj and proj:GetCurrentTimeline()
  if not tl then return { success = false, error = "No active timeline." } end
  local items = tl:GetItemListInTrack("video", tonumber(args.track_index or 1)) or {}
  local idx = tonumber(args.item_index or 1)
  if idx < 1 or idx > #items then return { success = false, error = "Item index out of range." } end
  local ok = items[idx]:SetCDL(args.cdl_map or {})
  return { success = ok and true or false }
end

handlers["add_color_version"] = function(args)
  local proj = pm:GetCurrentProject()
  local tl = proj and proj:GetCurrentTimeline()
  if not tl then return { success = false, error = "No active timeline." } end
  local items = tl:GetItemListInTrack("video", tonumber(args.track_index or 1)) or {}
  local idx = tonumber(args.item_index or 1)
  if idx < 1 or idx > #items then return { success = false, error = "Item index out of range." } end
  local ok = items[idx]:AddVersion(args.version_name, tonumber(args.version_type or 0))
  return { success = ok and true or false }
end

handlers["list_color_versions"] = function(args)
  local proj = pm:GetCurrentProject()
  local tl = proj and proj:GetCurrentTimeline()
  if not tl then return { success = false, error = "No active timeline." } end
  local items = tl:GetItemListInTrack("video", tonumber(args.track_index or 1)) or {}
  local idx = tonumber(args.item_index or 1)
  if idx < 1 or idx > #items then return { success = false, error = "Item index out of range." } end
  local versions = items[idx]:GetVersionNameList(tonumber(args.version_type or 0)) or {}
  return { success = true, versions = versions }
end

-- 7. Deliver & Render
handlers["get_render_presets"] = function(args)
  local proj = pm:GetCurrentProject()
  if not proj then return { success = false, error = "No project open." } end
  return { success = true, presets = proj:GetRenderPresetList() or {} }
end

handlers["load_render_preset"] = function(args)
  local proj = pm:GetCurrentProject()
  if not proj then return { success = false, error = "No project open." } end
  local ok = proj:LoadRenderPreset(args.preset_name)
  return { success = ok and true or false, preset_name = args.preset_name }
end

handlers["set_render_settings"] = function(args)
  local proj = pm:GetCurrentProject()
  if not proj then return { success = false, error = "No project open." } end
  local ok = proj:SetRenderSettings(args.settings or {})
  return { success = ok and true or false }
end

handlers["add_render_job"] = function(args)
  local proj = pm:GetCurrentProject()
  if not proj then return { success = false, error = "No project open." } end
  local id = proj:AddRenderJob()
  return { success = id ~= nil, job_id = id }
end

handlers["list_render_jobs"] = function(args)
  local proj = pm:GetCurrentProject()
  if not proj then return { success = false, error = "No project open." } end
  return { success = true, jobs = proj:GetRenderJobList() or {} }
end

handlers["start_rendering"] = function(args)
  local proj = pm:GetCurrentProject()
  if not proj then return { success = false, error = "No project open." } end
  local ok = proj:StartRendering()
  return { success = ok and true or false }
end

handlers["get_render_status"] = function(args)
  local proj = pm:GetCurrentProject()
  if not proj then return { success = false, error = "No project open." } end
  local job = proj:GetRenderJobStatus(args.job_id or "")
  return { success = true, status = job or {} }
end

handlers["stop_rendering"] = function(args)
  local proj = pm:GetCurrentProject()
  if not proj then return { success = false, error = "No project open." } end
  proj:StopRendering()
  return { success = true }
end

handlers["delete_all_render_jobs"] = function(args)
  local proj = pm:GetCurrentProject()
  if not proj then return { success = false, error = "No project open." } end
  local ok = proj:DeleteAllRenderJobs()
  return { success = ok and true or false }
end

--------------------------------------------------------------------------------
-- 5. Main Loop & IPC Dispatcher
--------------------------------------------------------------------------------
local function sleep(n)
  if bmd ~= nil and bmd.wait ~= nil then
    bmd.wait(n)
  elseif wait ~= nil then
    wait(n)
  else
    local t0 = os.clock()
    while os.clock() - t0 < n do end
  end
end

local function print_banner()
  local prod = dvr:GetProductName()
  local ver = dvr:GetVersionString()
  print("================================================================")
  print(" 🎬 DaVinci Resolve MCP In-App Lua Bridge (v" .. BRIDGE_VERSION .. ")")
  print("================================================================")
  print(" Product:      " .. prod)
  print(" Version:      " .. ver)
  print(" Transport:    File IPC (~/.davinci_resolve_mcp_ipc/)")
  print(" Status:       Active & Listening")
  print(" ")
  print(" ✅ Ready! Your AI assistant (Claude Desktop, Cursor, etc.) can")
  print("    now control DaVinci Resolve via native Lua!")
  print(" ")
  print(" (To stop: close DaVinci Resolve or create ~/.davinci_resolve_mcp_ipc/stop)")
  print("================================================================")
end

local function run_bridge()
  print_banner()
  write_status()

  local stop_file = ipc_dir .. sep .. "stop"
  -- Clear any previous stop signal
  os.remove(stop_file)

  local cycle = 0
  while true do
    -- Update status heartbeat every ~5 seconds (50 cycles * 0.1s)
    cycle = cycle + 1
    if cycle >= 50 then
      cycle = 0
      write_status()
    end

    -- Check for stop command
    local f_stop = io.open(stop_file, "r")
    if f_stop then
      f_stop:close()
      os.remove(stop_file)
      print("[DaVinci Resolve MCP Lua Bridge] Stop signal received. Exiting.")
      break
    end

    -- Check for incoming request
    local req_content = read_file(req_file)
    if req_content and #req_content > 0 then
      -- Remove request file so it's not reprocessed
      os.remove(req_file)

      local ok, req_data = pcall(json.decode, req_content)
      if ok and req_data and req_data.tool then
        local tool_name = req_data.tool
        local tool_args = req_data.kwargs or {}

        local handler = handlers[tool_name]
        local resp_data
        if handler then
          local exec_ok, exec_res = pcall(handler, tool_args)
          if exec_ok then
            resp_data = { success = true, result = exec_res }
          else
            resp_data = { success = false, error = "Error in tool '" .. tool_name .. "': " .. tostring(exec_res) }
          end
        else
          resp_data = { success = false, error = "Tool '" .. tool_name .. "' not found in Lua Bridge." }
        end

        local encoded_resp = json.encode(resp_data)
        -- Write atomic response
        local tmp_resp = resp_file .. ".tmp"
        write_file(tmp_resp, encoded_resp)
        os.remove(resp_file)
        os.rename(tmp_resp, resp_file)
      end
    end

    sleep(0.1)
  end
end

run_bridge()
