"""Read-only starter catalogue. Layouts are proposals, never factory or game-tested claims."""
import copy
from core import default_profile
from overlay_bindings import apply_reported_layout

CUSTOM_GAME='Custom / Other'
# Official references document controls or the game; none certifies this mapper.
GAMES={
 'Microsoft Flight Simulator 2024':dict(family='civil',url='https://flightsimulator.zendesk.com/hc/en-us/articles/16459737949980-Controller-Settings-FAQ',setup='Settings > Controls. Select the virtual gamepad, create a custom aircraft profile, and assign the outputs below. Aircraft/category profiles can override general bindings.'),
 'Microsoft Flight Simulator 2020':dict(family='civil',url='https://www.flightsimulator.com/accessibility/',setup='Open Control Options, select the virtual controller and create a custom profile. Check each aircraft control and remove conflicting automatic assignments.'),
 'X-Plane 12':dict(family='civil',url='https://x-plane.com/manuals/desktop/12/',setup='Open joystick settings, select the virtual controller, calibrate and bind the axes/buttons below. Aircraft profiles may require different assignments.'),
 'DCS World':dict(family='combat',url='https://www.digitalcombatsimulator.com/en/downloads/documentation/dcs-user_manual_en/',setup='Select your aircraft and control mode in Options > Controls. Bind the virtual-controller column and tune its axes. Module-specific actions differ; create a user preset for each aircraft.'),
 'IL-2 Sturmovik: Great Battles':dict(family='combat',url='https://il2sturmovik.com/news/856/update-5204/',setup='Use the game input/key-mapping settings to bind the virtual-controller axes and buttons. Aircraft engine and trim controls differ.'),
 'War Thunder':dict(family='combat',url='https://wiki.warthunder.com/controls/4785-setting-up-control-axis-and-sensitivity',setup='Select your desired aircraft control mode, configure axes and sensitivity, then bind the suggested actions. Simulator and assisted modes need different tuning.'),
 'Ace Combat 8: Wings of Theve':dict(family='arcade',url='https://www.bandainamcoent.com/games/ace-combat-8',setup='Use the game controller settings and verify pitch/roll, acceleration/deceleration, weapon and target controls. This proposed Xbox-output layout is not a verified AC8 factory preset.'),
 'Ace Combat 7: Skies Unknown':dict(family='arcade',url='https://www.bandainamcoent.com/games/ace-combat-7',setup='Use the controller configuration, verify your flight-control mode and map this app output to the game actions where supported. Verify trigger direction before flight.'),
 'Elite Dangerous':dict(family='space',url='https://www.elitedangerous.com/',setup='Create custom ship controls for the virtual controller. Bind pitch/roll/yaw, forward/reverse thrust and combat actions. Ship, SRV and on-foot controls are separate; this starter covers ship flight.'),
 'Star Citizen':dict(family='space',url='https://support.robertsspaceindustries.com/hc/en-us/articles/360000134267-Set-up-keybindings-for-your-peripherals',setup='Open Options > Keybindings > Advanced Controls Customization and select the virtual gamepad device. Bind ship actions below. Original-stick Joystick/HOTAS profiles are a different device and are not imported by this app.'),
 "No Man's Sky":dict(family='space',url='https://www.nomanssky.com/beyond-update/',setup='Review your PC gamepad configuration and ship flight controls. Bind/remap the available game actions where supported. The starter covers ship flight, not on-foot or VR controls.'),
 'Star Wars: Squadrons':dict(family='space',url='https://www.ea.com/able/resources/star-wars/star-wars-squadrons/pc/text-manual',setup='Open the controller remapping settings for the virtual gamepad and assign flight, throttle, weapons and power functions. Verify pitch/yaw/roll mode before using the starter.'),
 'EVERSPACE 2':dict(family='space',url='https://everspace-game.com/faq/',setup='Review the gamepad control scheme and custom bindings. Match flight/strafe and combat outputs below where supported; different control schemes swap axis roles.'),
 'Starfield':dict(family='space',url='https://help.bethesda.net/app/answers/detail/a_id/62149/~/does-starfield-have-controller-support-on-pc%3F',setup='Use the gamepad settings and ship-piloting controls. Match the supported flight/combat actions. This starter does not configure on-foot play or change game files.'),
 'X4: Foundations':dict(family='space',url='https://wiki.egosoft.com/X4%20Foundations%20Wiki/Manual%20and%20Guides/X4%3A%20Foundations%20Manual/',setup='Create a custom input profile for the virtual controller and bind ship steering, thrust and combat actions. Confirm flight-assist and throttle behavior in the game.'),
 'Space Engineers':dict(family='space',url='https://www.spaceengineersgame.com/',setup='Review the PC gamepad control layout and supported remapping. Match ship rotation, movement and toolbar actions where available. This starter is not a native HOTAS profile.'),
}

def starter_ids(game):
    return ('flight','look') if game in GAMES else ()

def starter_name(game,preset_id):
    if preset_id=='look':return 'H2 camera / look'
    family=GAMES[game]['family']
    return 'Ship flight / twist yaw' if family=='space' else 'Flight / twist rudder'

def make_starter(game,preset_id,current=None):
    if game not in GAMES or preset_id not in starter_ids(game):raise ValueError('Unknown game starter')
    p=apply_reported_layout(default_profile())
    # Retain measured direction/range and visual identities from the current V1.
    if current:p['physical'].update(copy.deepcopy(current.get('physical',{})))
    physical=p['physical'];family=GAMES[game]['family']
    p.update(game=game,name=starter_name(game,preset_id),preset_id=preset_id,preset_status='starter-unverified',mode='Xbox gamepad')
    def src(key):return copy.deepcopy(physical[key])
    p['outputs']={'LX':src('roll'),'LY':src('pitch'),'RT':src('lever_left'),'LT':src('lever_right')}
    # Existing uncalibrated pitch graphics are raw; invert the proposed output.
    if not current or current.get('calibration_version')!=1:p['outputs']['LY']['invert']=not p['outputs']['LY'].get('invert',False)
    if current and current.get('calibration_version')==1:p['calibration_version']=1
    p['outputs'].update(RX=src('H2_x') if preset_id=='look' else src('twist'),RY=src('H2_y'))
    for target,number in dict(A=18,B=1,X=16,Y=17,LB=2,RB=3,View=7,Menu=8,L3=15,R3=6).items():
        p['outputs'][target]=dict(kind='button',index=number-1)
    for target,direction in [('Up','up'),('Down','down'),('Left','left'),('Right','right')]:
        p['outputs'][target]=dict(kind='hat',index=0,direction=direction)
    roles={'LX':'Roll','LY':'Pitch','RX':'Camera X' if preset_id=='look' else 'Yaw / rudder','RY':'Camera Y' if preset_id=='look' else 'Auxiliary axis',
           'RT':'Forward thrust' if family=='space' else 'Throttle','LT':'Reverse thrust' if family=='space' else 'Brake',
           'Menu':'Pause / menu','View':'View / interface','L3':'Auxiliary action 1','R3':'Auxiliary action 2',
           'Up':'Utility up','Down':'Utility down','Left':'Utility left','Right':'Utility right'}
    if family=='civil':roles.update(A='Primary / brake action',B='Reset camera',X='Landing gear',Y='Flaps',LB='Trim decrease',RB='Trim increase')
    elif family=='space':roles.update(A='Primary fire / action',B='Target / interact',X='Secondary fire / action',Y='Boost / utility',LB='Utility left',RB='Utility right')
    else:roles.update(A='Primary fire',B='Target select',X='Secondary weapon',Y='Countermeasure / utility',LB='Utility left',RB='Utility right')
    if game=='Ace Combat 8: Wings of Theve':
        # Owner-confirmed Xbox scheme: right stick is look, bumpers are yaw.
        # Split the measured twist into mutually exclusive digital shoulders.
        p['outputs'].update(RX=src('H2_x'),RY=src('H2_y'))
        for target,half in (('LB','negative'),('RB','positive')):
            p['outputs'][target]=dict(src('twist'),range=half)
        roles.update(RX='Camera X',RY='Camera Y',LB='Yaw left / rudder',RB='Yaw right / rudder',
                     B='Fire secondary',X='Cycle weapons',Y='Change target')
    p['target_roles']=roles
    return p


def upgrade_legacy_action_labels(profile):
    """Correct only the old AC8 starter captions; preserve customized names/bindings."""
    p=copy.deepcopy(profile)
    if p.get('game')!='Ace Combat 8: Wings of Theve':return p
    roles=p.setdefault('target_roles',{})
    fixes={'RX':('Yaw / rudder','Camera X'),'RY':('Auxiliary axis','Camera Y'),
            'LB':('Utility left','Rudder left'),'RB':('Utility right','Rudder right'),
            'B':('Target select','Fire secondary'),'X':('Secondary weapon','Cycle weapons'),
            'Y':('Countermeasure / utility','Change target')}
    for target,(old,new) in fixes.items():
        if roles.get(target)==old:roles[target]=new
    return p
