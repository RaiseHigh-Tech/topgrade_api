# Video Upload - Review Step Validation

## ✅ Feature Added: Block Review Until Videos Uploaded

### What's New:
Users cannot proceed to the "Review" step in the wizard until all selected videos are uploaded to S3.

## 🔒 How It Works

### Add Program Wizard:
```
Step 1: General Info → ✓ Can proceed
Step 2: Other Details → ✓ Can proceed
Step 3: Syllabus → Select videos
  ├─ Video selected but not uploaded → ❌ Cannot go to Review
  └─ All videos uploaded → ✓ Can proceed to Review
Step 4: Review → ✓ Can submit
```

### Edit Program Wizard:
```
Step 1: General Info → ✓ Can proceed
Step 2: Other Details → ✓ Can proceed  
Step 3: Syllabus → Select/upload videos
  ├─ New video selected but not uploaded → ❌ Cannot go to Review
  └─ All videos uploaded or unchanged → ✓ Can proceed to Review
Step 4: Review → ✓ Can submit
```

## 🎯 User Experience

### Scenario 1: User Tries to Skip to Review Without Upload

**User Actions:**
1. User is on "Syllabus" tab
2. User selects video file for Topic 1
3. Upload button appears but user doesn't click it
4. User clicks "Next" to go to Review

**System Response:**
```
⚠️ Alert appears:
"Please upload all selected videos before submitting:
 • Module 1, Topic 1"

🔴 Upload button flashes RED for 3 seconds
❌ Navigation blocked - stays on Syllabus tab
```

### Scenario 2: User Uploads All Videos

**User Actions:**
1. User is on "Syllabus" tab
2. User selects video file for Topic 1
3. User clicks "Upload to S3" button
4. Progress bar completes → "✓ Video uploaded successfully!"
5. User clicks "Next" to go to Review

**System Response:**
```
✅ Validation passes
✅ Navigates to Review tab
✅ Can submit the form
```

## 📊 Validation States

| State | Videos Selected | Videos Uploaded | Can Go to Review | User Feedback |
|-------|----------------|-----------------|------------------|---------------|
| 1 | None | N/A | ✅ Yes | No videos is OK |
| 2 | Yes | None | ❌ No | Alert + Red button flash |
| 3 | Yes | Some | ❌ No | Alert listing pending videos |
| 4 | Yes | All | ✅ Yes | Proceed to Review |

## 🔧 Technical Implementation

### Navigation Button Click Handler

**Add Program Modal (Lines 1390-1398):**
```javascript
// Validate current tab before proceeding
if (!validateCurrentTab(currentTabContent)) {
    return false;
}

// Special validation: Check if moving to Review tab
if (nextTabId === 'pills-experience-tab') {
    // Validate that all selected videos are uploaded
    if (!validateVideosUploaded('programWizardForm')) {
        return false;  // Block navigation
    }
}
```

**Edit Program Modal (Lines 1796-1804):**
```javascript
// Validate current tab before proceeding
if (!validateEditCurrentTab(currentTabContent)) {
    return false;
}

// Special validation: Check if moving to Review tab
if (nextTabId === 'edit-pills-experience-tab') {
    // Validate that all selected videos are uploaded
    if (!validateVideosUploaded('editProgramWizardForm')) {
        return false;  // Block navigation
    }
}
```

### Validation Function (Already Exists)

The `validateVideosUploaded()` function handles:
- ✅ Checking all video file inputs
- ✅ Identifying videos selected but not uploaded
- ✅ Showing alert with specific modules/topics
- ✅ Flashing upload buttons in red
- ✅ Returning true/false for navigation control

## 🎨 Visual Feedback

### When Blocked:

**Alert Message:**
```
⚠️ Please upload all selected videos before submitting:

• Module 1, Topic 1
• Module 2, Topic 3

[OK]
```

**Upload Buttons:**
- Flash RED for 3 seconds
- Draw user attention to pending uploads
- Automatically return to green

**Navigation:**
- Stays on current tab (Syllabus)
- Does not proceed to Review
- User must upload videos first

## 📋 Edge Cases Handled

### Case 1: No Videos Selected
- **Action:** User skips video upload entirely
- **Result:** ✅ Can proceed to Review (videos are optional)

### Case 2: Existing Videos in Edit Mode
- **Action:** User edits program, doesn't change videos
- **Result:** ✅ Can proceed to Review (no new uploads needed)

### Case 3: Mix of Uploaded and Pending
- **Action:** Module 1 video uploaded, Module 2 not uploaded
- **Result:** ❌ Blocked, alert shows "Module 2, Topic X"

### Case 4: User Removes File After Selection
- **Action:** User selects file, then removes it (clears input)
- **Result:** ✅ Can proceed (no file selected = no upload needed)

### Case 5: Multiple Topics with Videos
- **Action:** 5 topics, 3 have videos, 1 uploaded, 2 pending
- **Result:** ❌ Blocked, alert shows 2 pending videos

## 🔄 Complete Flow

### Add Program:
```
1. General Info tab → Fill details
2. Other Details tab → Fill details
3. Syllabus tab:
   ├─ Add modules and topics
   ├─ Select video files
   ├─ Click "Upload to S3" for each
   └─ Wait for "✓ Video uploaded successfully!"
4. Click "Next" → Validation runs:
   ├─ If pending uploads → ❌ Alert + stay
   └─ If all uploaded → ✅ Go to Review
5. Review tab → Verify everything
6. Submit → Form submits
```

### Edit Program:
```
1. Open edit modal
2. Navigate to Syllabus tab
3. Select new video files (if changing)
4. Click "Upload to S3" for new videos
5. Click "Next" → Validation runs:
   ├─ If new uploads pending → ❌ Alert + stay
   └─ If all uploaded → ✅ Go to Review
6. Review tab → Verify changes
7. Submit → Form submits
```

## ✅ Benefits

### For Users:
- ✅ Clear feedback about what's blocking them
- ✅ Visual indicators (red buttons)
- ✅ Can't accidentally skip upload step
- ✅ Prevents form submission errors

### For Data Integrity:
- ✅ Ensures all videos are on S3
- ✅ No broken references in database
- ✅ Consistent data state
- ✅ No partial uploads

### For UX:
- ✅ Non-intrusive (only blocks if videos selected)
- ✅ Clear error messages
- ✅ Guides user to correct action
- ✅ Prevents confusion

## 🧪 Testing Scenarios

Test these cases:

- [ ] Add program, no videos → Can reach Review ✓
- [ ] Add program, select video, don't upload → Blocked at Syllabus
- [ ] Add program, upload all videos → Can reach Review ✓
- [ ] Edit program, no changes → Can reach Review ✓
- [ ] Edit program, add new video, don't upload → Blocked
- [ ] Edit program, upload new video → Can reach Review ✓
- [ ] Multiple videos, some uploaded → Blocked with list
- [ ] All videos uploaded → Can reach Review ✓

## 📝 Files Modified

1. **theme/templates/dashboard/programs.html**
   - Lines 1390-1398: Add wizard navigation validation
   - Lines 1796-1804: Edit wizard navigation validation
   - Uses existing `validateVideosUploaded()` function

## 🎉 Summary

### Before:
- Users could skip to Review without uploading videos
- Videos selected but not uploaded
- Form submission would fail or create broken data

### After:
- ✅ Review step blocked until all videos uploaded
- ✅ Clear feedback about pending uploads
- ✅ Visual indicators guide user
- ✅ Data integrity guaranteed

---

**Status:** ✅ Implemented  
**Applies To:** Both add and edit program wizards  
**User Impact:** Prevents errors, guides to correct flow  
**Date:** Current Session
