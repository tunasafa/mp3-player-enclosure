# Current DIY shopping list — touchscreen02

Revised 2026-10-08 after user chose **direct wires between XIAO ESP32-S3 Plus and Adafruit**, with hand assembly and no additional adapter PCB. Enclosure work is deferred. This is the current connection-shopping list; the mechanical BOM and older custom-carrier proposal describe different assemblies. No purchases or hardware tests have been performed.

**SD choice resolved at model level:** screenshot `Screenshot 2026-10-08 at 1.43.34.png` explicitly names **Adafruit 4682 Micro SD SPI or SDIO Card Breakout Board — 3V** and shows matching microSD socket/pin labels. This is the recommended SD model for the 3.3 V wiring below. The screenshot establishes the advertised model, not delivered seller authenticity; no additional 5 V supply is required by this board design.

## Latest checkout review — 02:03–02:04 cart

Inspected `Screenshot 2026-10-08 at 2.03.50.png` and `2.04.01.png`. Correct advertised models remain in the cart: XIAO ESP32-S3 Plus, Model5 capacitive screen, TLV320DAC3100 #6309, microSD #4682, 6P/18P sockets and protected 103450 battery candidate. **The screen's checkbox is now empty: select Model5 before checkout.** Both obsolete 12P audio ribbon packs are absent from these latest screenshots, resolving their earlier removal action.

The screenshots do not show the remaining small parts: four 47 ohm backlight resistors (1/8 W or greater), a small pack of 10 kilohm startup-pull resistors, a microSD card, the battery plug's actual mating JST-PH 2P/2.0 mm connector with insulated leads, or insulation/strain relief. Obtain these if not already owned, together with a USB-C data cable and assembly tools. For a physical battery on/off function, a suitably DC-rated latching switch in the battery harness is an additional final-player part; exact switch remains unselected. A simple battery disconnect does not turn off USB-powered operation and disconnects the battery from charging while open.

Wire remains 28 AWG two-core **shielded** cable. Gauge is acceptable for suitable short leads; individually insulated unshielded 28–30 AWG signal wire is preferable for the user's thin-routing goal. Battery remains a **4 PCS** option (now EUR17.12); only one is needed per player. These screenshots show the main models, not a complete assembly-consumables/tool inventory or hardware-tested player.

## Earlier checkout review — 01:51 cart and 01:58 socket drawing

Inspected `Screenshot 2026-10-08 at 1.51.06.png` and `1.51.33.png`. **The four advertised main models match the plan:** XIAO ESP32-S3 Plus, Model5 2.8-inch capacitive screen, TLV320DAC3100 #6309 and microSD breakout #4682. All four cart checkboxes are selected; the DAC is no longer unchecked. This is sufficient to recommend those models for development, not a hardware-tested complete player.

Before treating the whole cart as ready:

1. **Remove both selected 12P FFC packs.** Direct audio wires supersede them. The 12P loose-socket pack is no longer shown, which is correct.
2. **Keep the 6P and 18P socket options for the prototype.** User supplied [AliExpress item 1005004837108452](https://www.aliexpress.com/item/1005004837108452.html), then `Screenshot 2026-10-08 at 1.58.42.png` with the seller's technical drawing. It specifies **0.5 mm pitch** and **0.30 mm applicable FPC thickness**, matching the screen tails at nominal specification level and resolving the missing thickness evidence. Connector height is **2.00 ±0.1 mm**. The drawing gives no FPC thickness tolerance; delivered fit/contact engagement and pin numbering must still be checked before power. One socket of each count is needed; the five-piece packs provide spares. User intends direct hand-soldered socket wiring with mechanical support rather than a breakout PCB. The other two screenshots' generic specifications/AI overview add no useful mating evidence.
3. **Battery specification supplied; suitable candidate electrically.** Seller text provided by user identifies 103450 / 2000 mAh / nominal 3.7 V, charging up to 4.2 V, with overcharge, overdischarge, overcurrent and short-circuit protection. These match the required protected single-cell chemistry/voltage at specification level. Cart still selects `4 PCS/3.7 V/China Mainland`; use one pack per player and select 1PCS if available unless spares are wanted. Exact current/charging ratings and full-system load operation are not measured; protection is a seller claim. Enclosure size is deferred and is not a purchasing veto. The Plus's approximately 100 mA charge rate implies roughly 20 hours or more for an empty 2000 mAh pack, not fast charging. The AliExpress battery page remains unreadable through web tools; the user's pasted specification is the evidence.
4. **Add/ensure available:** four 47 ohm backlight resistors (initial dim prototype), 10 kilohm startup-pull resistors, suitable microSD card, insulation/strain relief, USB-C data cable and assembly tools. These are not visible in the screenshots and may already be owned.
5. **Battery harness is not plug-ready:** the battery title says JST-PH 2.0 mm, while the XIAO uses BAT+/BAT− solder pads. If retaining the battery plug, obtain its actual matching mating connector with insulated leads and verify polarity. A power-disconnect arrangement remains unselected. The battery protection PCB should not be interpreted as a standalone battery charger; use the XIAO charging provision.

Wire variant is now `28AWG-Black/2Cores/2meters`, as requested, but the title still says **shielded cable**. Its conductor gauge is reasonable for short internal low-current wiring; jacket/shield make it less convenient/thin than individual insulated wires. It can be used for suitable short leads if conductor material and insulation are appropriate; do not call it an unshielded hookup-wire product. Outer diameter/flexibility remain unverified.

## Keep / obtain for the first powered prototype

| Quantity | Item | Selected specification / status |
|---:|---|---|
| 1 | **Seeed XIAO ESP32-S3 Plus** | Cart option `ESP32S3 Plus 1PCS`, Sevenchip Hardware Store. Correct controller type; delivered authenticity/revision not verified. Keep headers off the thin hand-wired assembly. Install the supplied antenna. |
| 1 | **2.8-inch capacitive touchscreen, Model5** | Cart option `Model5`, Shop1104064300 Store. Earlier table identifies ST7789-family LCD + GT911 touch. User drawings show separate **18P/0.5 mm LCD** and **6P/0.5 mm touch** tails, 0.30 ±0.03 mm reinforced ends. Socket nominal pitch/thickness now match; exact delivered revision/initialization and physical mating are checked during bring-up. |
| 1 | **Adafruit TLV320DAC3100 #6309** | Cart title/photo match the intended headphone board; now selected in the 01:51 cart. Connect eight nets directly to the XIAO; no 12P audio cable/socket needed. |
| 1, from selected 5PCS pack | **18P/0.5 mm FPC ZIF socket** | Keep selected 18P option: seller drawing specifies 0.30 mm FPC and 2.00 ±0.1 mm socket height. Nominal pitch/thickness match the native LCD tail; no additional ribbon is needed. Verify contact engagement and numbering on receipt. Hand-soldering used contacts requires magnification, insulation, mechanical support and wire strain relief. |
| 1, from selected 5PCS pack | **6P/0.5 mm FPC ZIF socket** | Keep selected 6P option from the same documented family. Nominal pitch/thickness match the native touch tail; same receipt/assembly checks as 18P. |
| 1 | **Adafruit MicroSD SPI/SDIO breakout #4682 — 3V only** | Recommended replacement based on the `1.43.34` title/photo and manufacturer documentation: native **3.3 V power and logic**, no regulator or level shifter required. Use SPI mode and six direct wire connections. Leave supplied pin headers off for thin assembly. Delivered seller authenticity not verified. |
| 1 pack per player | **103450 protected 3.7 V / 2000 mAh lithium-polymer pack, 4.2 V full** | User-provided seller specification now confirms voltage and protection. Suitable battery candidate at specification level; current ratings/delivered performance unverified. Approximate 50 x 34 x 10 mm before any extra envelope allowance; enclosure deferred. Four-pack cart option is optional spares, not four cells required for the player. Expect slow charging from the XIAO. |
| 1 | **32 GB microSD card** | Authentic card; FAT32 for initial firmware bring-up. Use an existing suitable card if available. Test actual capacity/reliability after receipt. |
| Approximately 2 m supply | **28 AWG two-core insulated stranded-copper wire** | Suitable starting choice for short low-current power/ground leads; can also be split into individual insulated signal leads. Two cores provide only two independent nets. Actual outer diameter/flexibility matter to thickness; avoid bulky shielded cable. |
| Small spool, optional | **30 AWG individually insulated signal wire** | Easier to route/solder at closely spaced socket and XIAO pads than thicker cable. Several colors help identify signals. Short 28 AWG signal leads remain acceptable where practical. |
| 4, plus spares | **47 ohm resistors, 1/8 W or greater** | Initial lower-brightness backlight prototype only: one from each LED-K to GND, with LED-A at regulated 3.3 V. Not a validated final brightness setting. Confirm exact screen limits and measure current before increasing brightness. |
| Small pack | **10 kilohm resistors** | Available for reset-low/CS-high startup pulls if not already provided by the actual boards. Avoid adding conflicting pulls. |
| Small set | **Thin insulating sheet/tape and strain-relief materials** | Secure/insulate sockets and soldered wires without contaminating ribbon contacts or latches. |
| 1 if retaining the battery plug | **Verified matching battery connector with insulated leads** | Actual mating half for the battery's stated JST-PH 2P/2.0 mm connector; verify contact/housing match and polarity. Leads solder to XIAO BAT+/BAT−; it has no native battery plug socket. |
| 1 if not owned | **USB-C data cable** | USB-powered programming and initial tests; a charging-only cable is insufficient for data. |

Tools if not already owned: fine-tip soldering iron, flux, solder, tweezers, magnification and multimeter. A multimeter is needed to verify these hand-soldered connections; listing language calling it optional does not establish that the harness is correct.

Loose socket assembly follows the user's chosen no-extra-PCB route. The socket manufacturers normally specify PCB mounting; free-wired mechanical construction is not qualified here. Tiny ready-made passive breakout PCBs remain an optional easier alternative, not a required custom main board. Do not solder directly onto the screen's native flex tails.

## Remove from the audio shopping list

- **12P/0.5 mm loose sockets** (the CanHui `Lower contact/12P/0.5mm` pack).
- **12P/0.5 mm forward-direction FFC pack**.
- **12P/0.5 mm reverse-direction FFC pack**.
- Any extra **12P adapter/breakout boards**.
- The **32 AWG four-core shielded cable**, if replacing it with the simpler wire above.

No additional screen extension ribbons are required initially: use the screen's supplied 18P and 6P tails.

## Earlier SD listings — review history

The user's new description combines Micro TF, standard SD and MINI SD modules in one link. It says **4.5–5.5 V power input**, onboard 3.3 V regulation, and 3.3/5 V logic compatibility, but its wiring guide also says **VCC → 3.3 V for ESP32**. Those claims conflict. Do not interpret 3.3 V-compatible signals as proof that the regulator input accepts 3.3 V. A common description spanning three variants does not establish the selected mini module's circuit or supply range.

**New candidate, subsequent user message:** explicitly states **3.2–5.5 V operating voltage**, onboard 3.3 V LDO, 3.3/5 V-compatible SPI logic, and microSDHC up to 32 GB. These claimed specifications fit the intended 3.3 V supply and card size **on paper**, unlike the earlier 4.5–5.5 V claim. The presence of an LDO is not by itself a rejection criterion; its actual dropout/output under SD load matters. Listing link/selected option requested to establish the actual regulator, power path and level-shifter circuit. This new candidate is pending identification, not already purchased or hardware-qualified. For example, the [TI LM1117](https://www.ti.com/product/LM1117) needs voltage headroom; that reference does not identify the new module's regulator.

If the selected board really requires 4.5–5.5 V, it needs an appropriate 5 V supply. XIAO's USB-derived 5 V is unavailable on battery alone; adding a boost supply would increase parts and power-design work. If the selected mini board is actually a native 3.3 V module, the seller must supply variant-specific evidence to resolve the contradiction. Do not bypass an unknown regulator to force compatibility.

## Selected #4682 wiring in SPI mode

Do not follow an earlier listing's generic `GPIO19 / GPIO23 / GPIO18 / GPIO5` wiring example on the XIAO ESP32-S3 Plus. GPIO19 is used by native USB, and GPIO23 is not an ESP32-S3 GPIO. Use the following proposed map for **Adafruit #4682**, matching its actual pad labels:

| SD net | XIAO Plus | ESP32-S3 GPIO |
|---|---|---:|
| 3V | 3V3, regulated with adequate load margin | — |
| GND | Common GND | — |
| CLK (SCK) | D8 | 7 |
| SI / CMD (MOSI) | D10 | 9 |
| SO / D0 (MISO) | D9 | 8 |
| CS / D3 | D18, extra underside pad | 12 |

SD shares SCK/MOSI with the LCD, using separate CS signals. LCD SDO stays disconnected in this proposal. Firmware must configure the actual GPIOs and SPI sharing, rather than assume a board/library default map.

Leave module **D1, DAT2 and DET** disconnected for initial SPI operation; card detect is optional and would need a separate GPIO if used. Module `D3` is the alias of its **CS** pad, not an instruction to wire it to XIAO `D3`. Do not apply 5 V or battery voltage to the module's `3V` pad. Onboard pullups are provided on SPI pins.

Manufacturer examples/references: [native 3.3 V microSD breakout pinout](https://learn.adafruit.com/adafruit-microsd-spi-sdio/pinouts), [XIAO Plus pinout and power](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/), [Espressif ESP32-S3 pin definitions](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf). A documented reference design is not proof that a visually similar AliExpress module matches it. AliExpress discovery search: [3.3 V microSD SPI module](https://www.aliexpress.com/w/wholesale-3.3V-micro-SD-SPI-module.html); not a verified purchase link.

## Battery/final-player parts still open

For the first tests, use USB power. The user's protected 103450 / 2000 mAh / 3.7 V nominal / 4.2 V full pack is now a suitable candidate at advertised voltage/protection level. Battery harness, power-disconnect arrangement, current ratings and regulator-load margin still require selection/qualification. Do not reuse the old case-specific 1S2P requirement as a new ordering mandate. Do not substitute a 7.4 V/2S pack. No extra charger is selected while using the XIAO's charging provision. See [Seeed's battery and charging specification](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/); actual empty-to-full charging time depends on initial state, board revision, capacity and final charge phase.

Fixed low backlight brightness is the initial bring-up mode. Adjustable/full brightness requires a properly selected current-limiting/driver circuit and qualification. Additional physical controls have not been selected in this shopping list.

Full proposed signal connections are in [DIY_WIRING_GUIDE.md](DIY_WIRING_GUIDE.md). Correct protocols/pin allocations are a basis for testing, not a claim of perfect operation before assembly, reset/driver initialization and combined-load checks.
