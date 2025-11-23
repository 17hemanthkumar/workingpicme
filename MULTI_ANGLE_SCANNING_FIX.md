# Multi-Angle Face Scanning Implementation Fix

## Issue Fixed
The camera was only performing a single center face scan and skipping the left and right profile scans entirely.

## Solution Implemented
Updated `frontend/pages/biometric_authentication_portal.html` to implement the complete three-stage sequential scanning process.

## Changes Made

### 1. Multi-Stage Scanning State Management
Added state tracking for the three-stage scanning process:
```javascript
let currentStage = 0;
let capturedEncodings = [];
let stream = null;

const stages = [
    {
        name: 'center',
        instruction: 'Step 1/3: Please face the camera directly and keep your face centered',
        successMessage: '✓ Center face captured successfully!'
    },
    {
        name: 'left',
        instruction: 'Step 2/3: Please turn your head to the LEFT',
        successMessage: '✓ Left profile captured successfully!'
    },
    {
        name: 'right',
        instruction: 'Step 3/3: Please turn your head to the RIGHT',
        successMessage: '✓ Right profile captured successfully!'
    }
];
```

### 2. Sequential Scanning Flow
Implemented `startMultiAngleScanning()` function that:
- Displays clear instructions for each stage
- Gives user 4 seconds to position their head
- Captures the frame for that angle
- Shows success message
- Automatically advances to next stage
- Proceeds to recognition only after all 3 stages complete

### 3. Stage Capture Function
Created `captureStage()` function that:
- Captures the current video frame
- Stores the encoding with angle label (center, left, right)
- Shows success feedback
- Advances to next stage after 2-second pause

### 4. Finalization Process
Implemented `finalizeScanning()` function that:
- Stops the camera after all captures
- Sends all three encodings to backend
- Displays processing message

### 5. Updated UI
- Changed page title to "Multi-Angle Face Scan"
- Added description: "We'll capture your face from 3 angles for better recognition"
- Added stage indicator: "Center → Left Profile → Right Profile"

## How It Works Now

### User Experience Flow:
1. **Camera Initialization** (1.5 seconds)
   - "Initializing camera..."

2. **Stage 1: Center Face** (6 seconds total)
   - Display: "Step 1/3: Please face the camera directly and keep your face centered"
   - Wait 4 seconds for positioning
   - Capture center angle
   - Display: "✓ Center face captured successfully!"
   - Wait 2 seconds

3. **Stage 2: Left Profile** (6 seconds total)
   - Display: "Step 2/3: Please turn your head to the LEFT"
   - Wait 4 seconds for positioning
   - Capture left angle
   - Display: "✓ Left profile captured successfully!"
   - Wait 2 seconds

4. **Stage 3: Right Profile** (6 seconds total)
   - Display: "Step 3/3: Please turn your head to the RIGHT"
   - Wait 4 seconds for positioning
   - Capture right angle
   - Display: "✓ Right profile captured successfully!"
   - Wait 2 seconds

5. **Processing & Recognition**
   - Display: "All angles captured! Processing..."
   - Stop camera
   - Send all three encodings to backend
   - Display: "Verifying with multi-angle recognition..."
   - Redirect to photo gallery on success

**Total Time: ~21 seconds** (1.5s init + 3×6s stages + 2s processing)

## Data Sent to Backend

The frontend now sends all three captured angles to the `/recognize` endpoint:
```javascript
{
    image: centerEncoding.image,  // Primary image for backward compatibility
    event_id: eventId,
    multi_angle: true,             // Flag indicating multi-angle scan
    encodings: [                   // All three angle captures
        { angle: 'center', image: '...' },
        { angle: 'left', image: '...' },
        { angle: 'right', image: '...' }
    ]
}
```

## Benefits

✅ **Complete 3-angle capture** - Center, left, and right profiles all captured
✅ **Clear user guidance** - Step-by-step instructions with progress indicators
✅ **Visual feedback** - Success messages after each stage
✅ **Automatic progression** - No manual button clicks needed between stages
✅ **Better recognition** - Multiple angles enable matching with:
   - Partial/half-visible faces
   - Side profile photos
   - Faces at angles
   - Photos with accessories

## Testing

To test the multi-angle scanning:
1. Navigate to: http://127.0.0.1:5000/biometric_authentication_portal?event_id=event_931cd6b8
2. Allow camera access
3. Follow the on-screen instructions:
   - Face camera directly (center)
   - Turn head to the left
   - Turn head to the right
4. System will automatically capture all three angles and proceed to recognition

## Next Steps (Backend Enhancement)

The frontend now captures and sends all three angles. To fully utilize this data, the backend should be enhanced to:

1. **Store multi-angle encodings** - Save all three angles per user
2. **Weighted matching** - Use angle-appropriate weighting during recognition
3. **Enhanced recognition** - Match against all three stored angles for better accuracy

These backend enhancements are defined in the spec at:
- `.kiro/specs/multi-angle-face-recognition/requirements.md`
- `.kiro/specs/multi-angle-face-recognition/design.md`
- `.kiro/specs/multi-angle-face-recognition/tasks.md`

## Status

✅ **Frontend Implementation: COMPLETE**
- Three-stage sequential scanning implemented
- User guidance and progress indicators working
- All three angles captured and sent to backend

⏳ **Backend Integration: PENDING**
- Currently using center angle for recognition (backward compatible)
- Backend enhancement tasks available in spec for full multi-angle matching
